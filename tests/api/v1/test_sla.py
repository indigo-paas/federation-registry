import json
from datetime import date
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.config import get_settings
from app.sla.models import SLA
from app.sla.schemas import SLABase, SLARead, SLAReadShort
from app.sla.schemas_extended import SLAReadExtended
from tests.utils.sla import (
    create_random_sla_patch,
    validate_read_extended_sla_attrs,
    validate_read_short_sla_attrs,
    validate_read_sla_attrs,
)


def test_read_slas(
    db_sla2: SLA, db_sla3: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all slas."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_sla2.uid:
        resp_sla = content[0]
        resp_sla2 = content[1]
    else:
        resp_sla = content[1]
        resp_sla2 = content[0]

    validate_read_sla_attrs(obj_out=SLARead(**resp_sla), db_item=db_sla2)
    validate_read_sla_attrs(obj_out=SLARead(**resp_sla2), db_item=db_sla3)


def test_read_slas_with_target_params(
    db_sla: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all slas matching specific attributes passed as
    query attributes.
    """
    settings = get_settings()

    for k in SLABase.__fields__.keys():
        response = api_client_read_only.get(
            f"{settings.API_V1_STR}/slas/", params={k: db_sla.__getattribute__(k)}
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        validate_read_sla_attrs(obj_out=SLARead(**content[0]), db_item=db_sla)


def test_read_slas_with_limit(db_sla2: SLA, api_client_read_only: TestClient) -> None:
    """Execute GET operations to read all slas limiting the number of output items."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"limit": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"limit": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1


def test_read_sorted_slas(
    db_sla2: SLA, db_sla3: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all sorted slas."""
    settings = get_settings()
    sorted_items = sorted([db_sla2, db_sla3], key=lambda x: x.uid)

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"sort": "uid"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"sort": "-uid"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"sort": "uid_asc"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"sort": "uid_desc"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid


def test_read_slas_with_skip(db_sla2: SLA, api_client_read_only: TestClient) -> None:
    """Execute GET operations to read all slas, skipping the first N entries."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"skip": 0},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"skip": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"skip": 2},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"skip": 3},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_slas_with_pagination(
    db_sla2: SLA, db_sla3: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all slas.

    Paginate returned list.
    """
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"size": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    if content[0]["uid"] == db_sla2.uid:
        next_page_uid = db_sla3.uid
    else:
        next_page_uid = db_sla2.uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"size": 1, "page": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["uid"] == next_page_uid

    # Page greater than 0 but size equals None, does nothing
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/",
        params={"page": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    # Page index greater than maximum number of pages. Return nothing
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"size": 1, "page": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_slas_with_conn(
    db_sla2: SLA, db_sla3: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all slas with their relationships."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"with_conn": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_sla2.uid:
        resp_sla = content[0]
        resp_sla2 = content[1]
    else:
        resp_sla = content[1]
        resp_sla2 = content[0]

    validate_read_extended_sla_attrs(
        obj_out=SLAReadExtended(**resp_sla), db_item=db_sla2
    )
    validate_read_extended_sla_attrs(
        obj_out=SLAReadExtended(**resp_sla2), db_item=db_sla3
    )


def test_read_slas_short(
    db_sla2: SLA, db_sla3: SLA, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all slas with their shrunk version."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/", params={"short": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_sla2.uid:
        resp_sla = content[0]
        resp_sla2 = content[1]
    else:
        resp_sla = content[1]
        resp_sla2 = content[0]

    validate_read_short_sla_attrs(obj_out=SLAReadShort(**resp_sla), db_item=db_sla2)
    validate_read_short_sla_attrs(obj_out=SLAReadShort(**resp_sla2), db_item=db_sla3)


def test_read_sla(db_sla: SLA, api_client_read_only: TestClient) -> None:
    """Execute GET operations to read an SLA."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_sla_attrs(obj_out=SLARead(**content), db_item=db_sla)


def test_read_sla_with_conn(db_sla: SLA, api_client_read_only: TestClient) -> None:
    """Execute GET operations to read a public sla with its relationships."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}", params={"with_conn": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_extended_sla_attrs(obj_out=SLAReadExtended(**content), db_item=db_sla)


def test_read_sla_short(db_sla: SLA, api_client_read_only: TestClient) -> None:
    """Execute GET operations to read the shrunk version of an SLA."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}", params={"short": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_short_sla_attrs(obj_out=SLAReadShort(**content), db_item=db_sla)


def test_read_not_existing_sla(api_client_read_only: TestClient) -> None:
    """Execute GET operations to try to read a not existing sla."""
    settings = get_settings()
    item_uuid = uuid4()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/slas/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"SLA '{item_uuid}' not found"


def test_patch_sla(db_sla: SLA, api_client_read_write: TestClient) -> None:
    """Execute PATCH operations to update an SLA."""
    settings = get_settings()
    data = create_random_sla_patch()

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    for k, v in data.dict().items():
        if isinstance(v, date):
            v = v.isoformat()
        assert content[k] == v


def test_patch_sla_no_edit(db_sla: SLA, api_client_read_write: TestClient) -> None:
    """Execute PATCH operations to update a sla.

    Nothing changes.
    """
    settings = get_settings()
    data = create_random_sla_patch(default=True)

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}",
        json=json.loads(data.json(exclude_unset=True)),
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED


def test_patch_not_existing_sla(api_client_read_write: TestClient) -> None:
    """Execute PATCH operations to try to update a not existing sla."""
    settings = get_settings()
    item_uuid = uuid4()
    data = create_random_sla_patch()

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/slas/{item_uuid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"SLA '{item_uuid}' not found"


def test_patch_sla_with_duplicated_doc_uuid(
    db_sla: SLA, db_sla3: SLA, api_client_read_write: TestClient
) -> None:
    """Execute PATCH operations to try to assign an already existing UUID to an SLA."""
    settings = get_settings()
    data = create_random_sla_patch()
    data.doc_uuid = db_sla.doc_uuid

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/slas/{db_sla3.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert (
        content["detail"] == f"Document '{data.doc_uuid}' already used by another SLA"
    )


# TODO Add tests raising 422


def test_delete_sla(db_sla: SLA, api_client_read_write: TestClient) -> None:
    """Execute DELETE to remove an SLA."""
    settings = get_settings()
    response = api_client_read_write.delete(
        f"{settings.API_V1_STR}/slas/{db_sla.uid}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_not_existing_sla(api_client_read_write: TestClient) -> None:
    """Execute DELETE operations to try to delete a not existing sla."""
    settings = get_settings()
    item_uuid = uuid4()
    response = api_client_read_write.delete(
        f"{settings.API_V1_STR}/slas/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"SLA '{item_uuid}' not found"
