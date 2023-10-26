import json
from typing import Dict
from uuid import uuid4

from app.config import get_settings
from app.user_group.models import UserGroup
from app.user_group.schemas import UserGroupBase, UserGroupRead, UserGroupReadShort
from app.user_group.schemas_extended import UserGroupReadExtended
from fastapi import status
from fastapi.testclient import TestClient
from tests.utils.user_group import (
    create_random_user_group_patch,
    validate_read_extended_user_group_attrs,
    validate_read_short_user_group_attrs,
    validate_read_user_group_attrs,
)


def test_read_user_groups(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups."""
    settings = get_settings()

    response = client.get(f"{settings.API_V1_STR}/user_groups/", headers=read_header)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_user_group.uid:
        resp_user = content[0]
        resp_user2 = content[1]
    else:
        resp_user = content[1]
        resp_user2 = content[0]

    validate_read_user_group_attrs(
        obj_out=UserGroupRead(**resp_user), db_item=db_user_group
    )
    validate_read_user_group_attrs(
        obj_out=UserGroupRead(**resp_user2), db_item=db_user_group2
    )


def test_read_user_groups_with_target_params(
    db_user_group: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups matching specific
    attributes passed as query attributes."""
    settings = get_settings()

    for k in UserGroupBase.__fields__.keys():
        response = client.get(
            f"{settings.API_V1_STR}/user_groups/",
            params={k: db_user_group.__getattribute__(k)},
            headers=read_header,
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        validate_read_user_group_attrs(
            obj_out=UserGroupRead(**content[0]), db_item=db_user_group
        )


def test_read_user_groups_with_limit(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups limiting the number of
    output items."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"limit": 0},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"limit": 1},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1


def test_read_sorted_user_groups(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all sorted user_groups."""
    settings = get_settings()
    sorted_items = list(sorted([db_user_group, db_user_group2], key=lambda x: x.uid))

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"sort": "uid"},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"sort": "-uid"},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"sort": "uid_asc"},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"sort": "uid_desc"},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid


def test_read_user_groups_with_skip(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups, skipping the first N
    entries."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"skip": 0},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"skip": 1},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"skip": 2},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"skip": 3},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_user_groups_with_pagination(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups.

    Paginate returned list.
    """
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"size": 1},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    if content[0]["uid"] == db_user_group.uid:
        next_page_uid = db_user_group2.uid
    else:
        next_page_uid = db_user_group.uid

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"size": 1, "page": 1},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["uid"] == next_page_uid

    # Page greater than 0 but size equals None, does nothing
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"page": 1},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    # Page index greater than maximum number of pages. Return nothing
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"size": 1, "page": 2},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_user_groups_with_conn(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups with their
    relationships."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"with_conn": True},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_user_group.uid:
        resp_user = content[0]
        resp_user2 = content[1]
    else:
        resp_user = content[1]
        resp_user2 = content[0]

    validate_read_extended_user_group_attrs(
        obj_out=UserGroupReadExtended(**resp_user), db_item=db_user_group
    )
    validate_read_extended_user_group_attrs(
        obj_out=UserGroupReadExtended(**resp_user2), db_item=db_user_group2
    )


def test_read_user_groups_short(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read all user_groups with their shrunk
    version."""
    settings = get_settings()

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/",
        params={"short": True},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_user_group.uid:
        resp_user = content[0]
        resp_user2 = content[1]
    else:
        resp_user = content[1]
        resp_user2 = content[0]

    validate_read_short_user_group_attrs(
        obj_out=UserGroupReadShort(**resp_user), db_item=db_user_group
    )
    validate_read_short_user_group_attrs(
        obj_out=UserGroupReadShort(**resp_user2), db_item=db_user_group2
    )


def test_read_user_group(
    db_user_group: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read a user_group."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{db_user_group.uid}",
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_user_group_attrs(
        obj_out=UserGroupRead(**content), db_item=db_user_group
    )


def test_read_user_group_with_conn(
    db_user_group: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read a user_group with its relationships."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{db_user_group.uid}",
        params={"with_conn": True},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_extended_user_group_attrs(
        obj_out=UserGroupReadExtended(**content), db_item=db_user_group
    )


def test_read_user_group_short(
    db_user_group: UserGroup,
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to read the shrunk version of a user_group."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{db_user_group.uid}",
        params={"short": True},
        headers=read_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_short_user_group_attrs(
        obj_out=UserGroupReadShort(**content), db_item=db_user_group
    )


def test_read_not_existing_user_group(
    client: TestClient,
    read_header: Dict,
) -> None:
    """Execute GET operations to try to read a not existing user_group."""
    settings = get_settings()
    item_uuid = uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{item_uuid}", headers=read_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"User Group '{item_uuid}' not found"


def test_patch_user_group(
    db_user_group: UserGroup,
    client: TestClient,
    write_header: Dict,
) -> None:
    """Execute PATCH operations to update a user_group."""
    settings = get_settings()
    data = create_random_user_group_patch()

    response = client.patch(
        f"{settings.API_V1_STR}/user_groups/{db_user_group.uid}",
        json=json.loads(data.json()),
        headers=write_header,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    for k, v in data.dict().items():
        assert content[k] == v


def test_patch_not_existing_user_group(
    client: TestClient,
    write_header: Dict,
) -> None:
    """Execute PATCH operations to try to update a not existing user_group."""
    settings = get_settings()
    item_uuid = uuid4()
    data = create_random_user_group_patch()

    response = client.patch(
        f"{settings.API_V1_STR}/user_groups/{item_uuid}",
        json=json.loads(data.json()),
        headers=write_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"User Group '{item_uuid}' not found"


def test_patch_user_group_with_duplicated_name(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    write_header: Dict,
) -> None:
    """Execute PATCH operations to try to assign an already existing name to a
    user_group."""
    settings = get_settings()
    data = create_random_user_group_patch()
    data.name = db_user_group.name

    response = client.patch(
        f"{settings.API_V1_STR}/user_groups/{db_user_group2.uid}",
        json=json.loads(data.json()),
        headers=write_header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["detail"] == f"User Group with name '{data.name}' already registered"


# TODO Add tests raising 422


def test_delete_user_group(
    db_user_group: UserGroup,
    db_user_group2: UserGroup,
    client: TestClient,
    write_header: Dict,
) -> None:
    """Execute DELETE to remove a public user_group."""
    settings = get_settings()
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{db_user_group.uid}",
        headers=write_header,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_not_existing_user_group(
    client: TestClient,
    write_header: Dict,
) -> None:
    """Execute DELETE operations to try to delete a not existing user_group."""
    settings = get_settings()
    item_uuid = uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{item_uuid}", headers=write_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"User Group '{item_uuid}' not found"