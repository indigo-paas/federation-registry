from typing import Any, Dict, List, Literal, Tuple
from unittest.mock import Mock, PropertyMock, patch
from uuid import uuid4

import pytest
from neo4j.graph import Node
from neomodel import RelationshipManager, RequiredProperty
from pytest_cases import parametrize, parametrize_with_cases

from app.image.models import Image
from tests.common.utils import random_lower_string


class CaseMissing:
    @parametrize(value=["name", "uuid"])
    def case_missing(self, value: str) -> str:
        return value


class CaseAttr:
    @parametrize(
        key=[
            "description",
            "os_type",
            "os_distro",
            "os_version",
            "architecture",
            "kernel_id",
        ]
    )
    def case_str(self, key: str) -> Tuple[str, str]:
        return key, random_lower_string()

    @parametrize(key=["cuda_support", "gpu_driver", "is_public"])
    def case_bool(self, key: str) -> Tuple[str, Literal[True]]:
        return key, True

    @parametrize(key=["empty", "full"])
    def case_list_str(self, key: str) -> Tuple[str, List[str]]:
        if key == "empty":
            return key, []
        return key, [random_lower_string()]


def image_dict() -> Dict[str, str]:
    return {"name": random_lower_string(), "uuid": uuid4().hex}


def test_default_attr() -> None:
    d = image_dict()
    item = Image(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.is_public is True
    assert item.os_type is None
    assert item.os_distro is None
    assert item.os_version is None
    assert item.architecture is None
    assert item.kernel_id is None
    assert item.cuda_support is False
    assert item.gpu_driver is False
    assert item.tags is None
    assert isinstance(item.projects, RelationshipManager)
    assert isinstance(item.services, RelationshipManager)


@parametrize_with_cases("missing_attr", cases=CaseMissing)
def test_missing_attr(missing_attr: str) -> None:
    d = image_dict()
    d[missing_attr] = None
    item = Image(**d)
    with pytest.raises(RequiredProperty):
        item.save()


@patch("neomodel.core.db")
@parametrize_with_cases("key, value", cases=CaseAttr)
def test_attr(mock_db: Mock, key: str, value: Any) -> None:
    d = image_dict()
    d[key] = value

    db_version = "5"
    type(mock_db).database_version = PropertyMock(return_value=db_version)
    element_id = f"{db_version}:{uuid4().hex}:0"
    mock_db.cypher_query.return_value = (
        [[Node(..., element_id=element_id, id_=0, properties=d)]],
        None,
    )

    item = Image(**d)
    saved = item.save()

    assert saved.element_id_property == element_id
    assert saved.uid == item.uid
    assert saved.__getattribute__(key) == value
