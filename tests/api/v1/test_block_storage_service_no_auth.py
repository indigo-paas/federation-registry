import json
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.config import get_settings
from app.service.models import BlockStorageService
from app.service.schemas import (
    BlockStorageServiceBase,
    BlockStorageServiceReadPublic,
)
from app.service.schemas_extended import BlockStorageServiceReadExtendedPublic
from tests.utils.block_storage_service import (
    create_random_block_storage_service_patch,
    validate_read_extended_public_block_storage_service_attrs,
    validate_read_public_block_storage_service_attrs,
)


def test_read_block_storage_services(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_block_storage_serv.uid:
        resp_bs_serv = content[0]
        resp_bs_serv2 = content[1]
    else:
        resp_bs_serv = content[1]
        resp_bs_serv2 = content[0]

    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**resp_bs_serv),
        db_item=db_block_storage_serv,
    )
    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**resp_bs_serv2),
        db_item=db_block_storage_serv2,
    )


def test_read_block_storage_services_with_target_params(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services matching specific
    attributes passed as query attributes.
    """
    settings = get_settings()

    for k in BlockStorageServiceBase.__fields__.keys():
        response = client.get(
            f"{settings.API_V1_STR}/block_storage_services/",
            params={k: db_block_storage_serv.__getattribute__(k)},
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        validate_read_public_block_storage_service_attrs(
            obj_out=BlockStorageServiceReadPublic(**content[0]),
            db_item=db_block_storage_serv,
        )


def test_read_block_storage_services_with_limit(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services limiting the number of
    output items.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"limit": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"limit": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1


def test_read_sorted_block_storage_services(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all sorted block_storage_services."""
    settings = get_settings()
    sorted_items = sorted(
        [db_block_storage_serv, db_block_storage_serv2],
        key=lambda x: x.uid,
    )

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"sort": "uid"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"sort": "-uid"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"sort": "uid_asc"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"sort": "uid_desc"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid


def test_read_block_storage_services_with_skip(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services, skipping the first N
    entries.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"skip": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"skip": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"skip": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"skip": 3}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_block_storage_services_with_pagination(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services.

    Paginate returned list.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"size": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    if content[0]["uid"] == db_block_storage_serv.uid:
        next_page_uid = db_block_storage_serv2.uid
    else:
        next_page_uid = db_block_storage_serv.uid

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"size": 1, "page": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["uid"] == next_page_uid

    # Page greater than 0 but size equals None, does nothing
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/", params={"page": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    # Page index greater than maximum number of pages. Return nothing
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"size": 1, "page": 2},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_block_storage_services_with_conn(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services with their
    relationships.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"with_conn": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_block_storage_serv.uid:
        resp_bs_serv = content[0]
        resp_bs_serv2 = content[1]
    else:
        resp_bs_serv = content[1]
        resp_bs_serv2 = content[0]

    validate_read_extended_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadExtendedPublic(**resp_bs_serv),
        db_item=db_block_storage_serv,
    )
    validate_read_extended_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadExtendedPublic(**resp_bs_serv2),
        db_item=db_block_storage_serv2,
    )


def test_read_block_storage_services_short(
    db_block_storage_serv: BlockStorageService,
    db_block_storage_serv2: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read all block_storage_services with their shrunk
    version.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/",
        params={"short": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_block_storage_serv.uid:
        resp_bs_serv = content[0]
        resp_bs_serv2 = content[1]
    else:
        resp_bs_serv = content[1]
        resp_bs_serv2 = content[0]

    # TODO
    # with pytest.raises(ValidationError):
    #     q = BlockStorageServiceReadShort(**resp_bs_serv)
    # with pytest.raises(ValidationError):
    #     q = BlockStorageServiceReadShort(**resp_bs_serv2)

    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**resp_bs_serv),
        db_item=db_block_storage_serv,
    )
    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**resp_bs_serv2),
        db_item=db_block_storage_serv2,
    )


def test_read_block_storage_service(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read a block_storage_service."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/{db_block_storage_serv.uid}",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**content),
        db_item=db_block_storage_serv,
    )


def test_read_block_storage_service_with_conn(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read a block_storage_service with its relationships."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/{db_block_storage_serv.uid}",
        params={"with_conn": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_extended_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadExtendedPublic(**content),
        db_item=db_block_storage_serv,
    )


def test_read_block_storage_service_short(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute GET operations to read the shrunk version of a block_storage_service."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/{db_block_storage_serv.uid}",
        params={"short": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()

    # TODO
    # with pytest.raises(ValidationError):
    #     q = BlockStorageServiceReadShort(**content)

    validate_read_public_block_storage_service_attrs(
        obj_out=BlockStorageServiceReadPublic(**content),
        db_item=db_block_storage_serv,
    )


def test_read_not_existing_block_storage_service(
    client: TestClient,
) -> None:
    """Execute GET operations to try to read a not existing block_storage_service."""
    settings = get_settings()
    item_uuid = uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/block_storage_services/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"Block Storage Service '{item_uuid}' not found"


def test_patch_block_storage_service(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a block_storage_service.

    No access rights. Permission denied
    """
    settings = get_settings()
    data = create_random_block_storage_service_patch()
    response = client.patch(
        f"{settings.API_V1_STR}/block_storage_services/{db_block_storage_serv.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_patch_not_existing_block_storage_service(
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a not existing block_storage_service.

    No access rights. Permission denied
    """
    settings = get_settings()
    data = create_random_block_storage_service_patch()
    response = client.patch(
        f"{settings.API_V1_STR}/block_storage_services/{uuid4()}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_delete_block_storage_service(
    db_block_storage_serv: BlockStorageService,
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a block_storage_service.

    No access rights. Permission denied
    """
    settings = get_settings()
    response = client.delete(
        f"{settings.API_V1_STR}/block_storage_services/{db_block_storage_serv.uid}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_delete_not_existing_block_storage_service(
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a not existing block_storage_service.

    No access rights. Permission denied
    """
    settings = get_settings()
    response = client.delete(f"{settings.API_V1_STR}/block_storage_services/{uuid4()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"
