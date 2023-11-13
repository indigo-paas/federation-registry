import json
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.config import get_settings
from app.region.models import Region
from app.region.schemas import RegionBase, RegionReadPublic
from app.region.schemas_extended import RegionReadExtendedPublic
from tests.utils.region import (
    create_random_region_patch,
    validate_read_extended_public_region_attrs,
    validate_read_public_region_attrs,
)


def test_read_regions(
    db_region2: Region,
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/regions/",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_region2.uid:
        resp_reg = content[0]
        resp_reg2 = content[1]
    else:
        resp_reg = content[1]
        resp_reg2 = content[0]

    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**resp_reg), db_item=db_region2
    )
    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**resp_reg2), db_item=db_region3
    )


def test_read_regions_with_target_params(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions matching specific attributes passed as
    query attributes.
    """
    settings = get_settings()

    for k in RegionBase.__fields__.keys():
        response = client.get(
            f"{settings.API_V1_STR}/regions/",
            params={k: db_region.__getattribute__(k)},
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        validate_read_public_region_attrs(
            obj_out=RegionReadPublic(**content[0]), db_item=db_region
        )


def test_read_regions_with_limit(
    db_region2: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions limiting the number of output
    items.
    """
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"limit": 0})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"limit": 1})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1


def test_read_sorted_regions(
    db_region2: Region,
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all sorted regions."""
    settings = get_settings()
    sorted_items = sorted([db_region2, db_region3], key=lambda x: x.uid)

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"sort": "uid"})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"sort": "-uid"})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"sort": "uid_asc"})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(
        f"{settings.API_V1_STR}/regions/",
        params={"sort": "uid_desc"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid


def test_read_regions_with_skip(
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions, skipping the first N entries."""
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"skip": 0})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"skip": 1})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"skip": 2})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"skip": 3})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_regions_with_pagination(
    db_region2: Region,
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions.

    Paginate returned list.
    """
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"size": 1})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    if content[0]["uid"] == db_region2.uid:
        next_page_uid = db_region3.uid
    else:
        next_page_uid = db_region2.uid

    response = client.get(
        f"{settings.API_V1_STR}/regions/", params={"size": 1, "page": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["uid"] == next_page_uid

    # Page greater than 0 but size equals None, does nothing
    response = client.get(f"{settings.API_V1_STR}/regions/", params={"page": 1})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    # Page index greater than maximum number of pages. Return nothing
    response = client.get(
        f"{settings.API_V1_STR}/regions/", params={"size": 1, "page": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_regions_with_conn(
    db_region2: Region,
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions with their relationships."""
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"with_conn": True})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_region2.uid:
        resp_reg = content[0]
        resp_reg2 = content[1]
    else:
        resp_reg = content[1]
        resp_reg2 = content[0]

    validate_read_extended_public_region_attrs(
        obj_out=RegionReadExtendedPublic(**resp_reg),
        db_item=db_region2,
    )
    validate_read_extended_public_region_attrs(
        obj_out=RegionReadExtendedPublic(**resp_reg2),
        db_item=db_region3,
    )


def test_read_regions_short(
    db_region2: Region,
    db_region3: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read all regions with their shrunk version."""
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/regions/", params={"short": True})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_region2.uid:
        resp_reg = content[0]
        resp_reg2 = content[1]
    else:
        resp_reg = content[1]
        resp_reg2 = content[0]

    # TODO
    # with pytest.raises(ValidationError):
    #     q = RegionReadShort(**resp_reg)
    # with pytest.raises(ValidationError):
    #     q = RegionReadShort(**resp_reg2)

    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**resp_reg), db_item=db_region2
    )
    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**resp_reg2), db_item=db_region3
    )


def test_read_region(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read a region."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/regions/{db_region.uid}",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**content), db_item=db_region
    )


def test_read_region_with_conn(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read a region with its relationships."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/regions/{db_region.uid}",
        params={"with_conn": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_extended_public_region_attrs(
        obj_out=RegionReadExtendedPublic(**content), db_item=db_region
    )


def test_read_region_short(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute GET operations to read the shrunk version of a region."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/regions/{db_region.uid}",
        params={"short": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()

    # TODO
    # with pytest.raises(ValidationError):
    #     q = RegionReadShort(**content)

    validate_read_public_region_attrs(
        obj_out=RegionReadPublic(**content), db_item=db_region
    )


def test_read_not_existing_region(
    client: TestClient,
) -> None:
    """Execute GET operations to try to read a not existing region."""
    settings = get_settings()
    item_uuid = uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/regions/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"Region '{item_uuid}' not found"


def test_patch_region(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a region.

    No access rights. Permission denied
    """
    settings = get_settings()
    data = create_random_region_patch()
    response = client.patch(
        f"{settings.API_V1_STR}/regions/{db_region.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_patch_not_existing_region(
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a not existing region.

    No access rights. Permission denied
    """
    settings = get_settings()
    data = create_random_region_patch()
    response = client.patch(
        f"{settings.API_V1_STR}/regions/{uuid4()}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_delete_region(
    db_region: Region,
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a region.

    No access rights. Permission denied
    """
    settings = get_settings()
    response = client.delete(f"{settings.API_V1_STR}/regions/{db_region.uid}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"


def test_delete_not_existing_region(
    client: TestClient,
) -> None:
    """Execute PATCH operations to update a not existing region.

    No access rights. Permission denied
    """
    settings = get_settings()
    response = client.delete(f"{settings.API_V1_STR}/regions/{uuid4()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert content["detail"] == "Not authenticated"
