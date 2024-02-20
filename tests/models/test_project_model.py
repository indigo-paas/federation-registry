from typing import Any, Dict, Tuple
from unittest.mock import Mock, PropertyMock, patch
from uuid import uuid4

import pytest
from neo4j.graph import Node
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize, parametrize_with_cases

from fed_reg.project.models import Project
from tests.utils import random_lower_string


class CaseMissing:
    @parametrize(value=["name", "uuid"])
    def case_missing(self, value: str) -> str:
        return value


class CaseAttr:
    @parametrize(key=["description"])
    def case_str(self, key: str) -> Tuple[str, str]:
        return key, random_lower_string()


def project_dict() -> Dict[str, str]:
    return {"name": random_lower_string(), "uuid": uuid4().hex}


def test_default_attr() -> None:
    d = project_dict()
    item = Project(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert isinstance(item.sla, RelationshipManager)
    assert isinstance(item.provider, RelationshipManager)
    assert isinstance(item.quotas, RelationshipManager)
    assert isinstance(item.private_flavors, RelationshipManager)
    assert isinstance(item.private_images, RelationshipManager)
    assert isinstance(item.private_networks, RelationshipManager)


@parametrize_with_cases("missing_attr", cases=CaseMissing)
def test_missing_attr(missing_attr: str) -> None:
    d = project_dict()
    d[missing_attr] = None
    item = Project(**d)
    with pytest.raises(RequiredProperty):
        item.save()


@patch("neomodel.core.db")
@parametrize_with_cases("key, value", cases=CaseAttr)
def test_attr(mock_db: Mock, key: str, value: Any) -> None:
    d = project_dict()
    d[key] = value

    db_version = "5"
    type(mock_db).database_version = PropertyMock(return_value=db_version)
    element_id = f"{db_version}:{uuid4().hex}:0"
    mock_db.cypher_query.return_value = (
        [[Node(..., element_id=element_id, id_=0, properties=d)]],
        None,
    )

    item = Project(**d)
    saved = item.save()

    assert saved.element_id_property == element_id
    assert saved.uid == item.uid
    assert saved.__getattribute__(key) == value


@patch("neomodel.match.db")
def test_required_rel(mock_db: Mock) -> None:
    db_version = "5"
    type(mock_db).database_version = PropertyMock(return_value=db_version)
    mock_db.cypher_query.return_value = ([], None)

    item = Project(**project_dict())
    with pytest.raises(CardinalityViolation):
        item.provider.all()
    with pytest.raises(CardinalityViolation):
        item.provider.single()


@patch("neomodel.match.db")
def test_optional_rel(mock_db: Mock) -> None:
    db_version = "5"
    type(mock_db).database_version = PropertyMock(return_value=db_version)
    mock_db.cypher_query.return_value = ([], None)

    item = Project(**project_dict())
    assert len(item.sla.all()) == 0
    assert item.sla.single() is None
    assert len(item.quotas.all()) == 0
    assert item.quotas.single() is None
    assert len(item.private_flavors.all()) == 0
    assert item.private_flavors.single() is None
    assert len(item.private_images.all()) == 0
    assert item.private_images.single() is None
    assert len(item.private_networks.all()) == 0
    assert item.private_networks.single() is None


# TODO test public_flavors
# TODO test public_images
# TODO test public_networks