import json
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.config import get_settings
from app.provider.models import Provider
from app.provider.schemas import ProviderBase, ProviderRead, ProviderReadShort
from app.provider.schemas_extended import ProviderReadExtended
from tests.utils.provider import (
    create_random_provider_patch,
    validate_read_extended_provider_attrs,
    validate_read_provider_attrs,
    validate_read_short_provider_attrs,
)


def test_read_providers(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_provider_with_single_project.uid:
        resp_prov = content[0]
        resp_prov2 = content[1]
    else:
        resp_prov = content[1]
        resp_prov2 = content[0]

    validate_read_provider_attrs(
        obj_out=ProviderRead(**resp_prov),
        db_item=db_provider_with_single_project,
    )
    validate_read_provider_attrs(
        obj_out=ProviderRead(**resp_prov2),
        db_item=db_provider_with_multiple_projects,
    )


def test_read_providers_with_target_params(
    db_provider_with_single_project: Provider, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read all providers matching specific attributes passed
    as query attributes.
    """
    settings = get_settings()

    for k in ProviderBase.__fields__.keys():
        response = api_client_read_only.get(
            f"{settings.API_V1_STR}/providers/",
            params={k: db_provider_with_single_project.__getattribute__(k)},
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        validate_read_provider_attrs(
            obj_out=ProviderRead(**content[0]),
            db_item=db_provider_with_single_project,
        )


def test_read_providers_with_limit(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers limiting the number of output
    items.
    """
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"limit": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"limit": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1


def test_read_sorted_providers(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all sorted providers."""
    settings = get_settings()
    sorted_items = sorted(
        [
            db_provider_with_single_project,
            db_provider_with_multiple_projects,
        ],
        key=lambda x: x.uid,
    )

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"sort": "uid"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"sort": "-uid"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"sort": "uid_asc"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[0].uid
    assert content[1]["uid"] == sorted_items[1].uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"sort": "uid_desc"}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2
    assert content[0]["uid"] == sorted_items[1].uid
    assert content[1]["uid"] == sorted_items[0].uid


def test_read_providers_with_skip(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers, skipping the first N entries."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"skip": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"skip": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"skip": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"skip": 3}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_providers_with_pagination(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers.

    Paginate returned list.
    """
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"size": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    if content[0]["uid"] == db_provider_with_single_project.uid:
        next_page_uid = db_provider_with_multiple_projects.uid
    else:
        next_page_uid = db_provider_with_single_project.uid

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"size": 1, "page": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["uid"] == next_page_uid

    # Page greater than 0 but size equals None, does nothing
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"page": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    # Page index greater than maximum number of pages. Return nothing
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"size": 1, "page": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 0


def test_read_providers_with_conn(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers with their relationships."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"with_conn": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_provider_with_single_project.uid:
        resp_prov = content[0]
        resp_prov2 = content[1]
    else:
        resp_prov = content[1]
        resp_prov2 = content[0]

    validate_read_extended_provider_attrs(
        obj_out=ProviderReadExtended(**resp_prov),
        db_item=db_provider_with_single_project,
    )
    validate_read_extended_provider_attrs(
        obj_out=ProviderReadExtended(**resp_prov2),
        db_item=db_provider_with_multiple_projects,
    )


def test_read_providers_short(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_only: TestClient,
) -> None:
    """Execute GET operations to read all providers with their shrunk version."""
    settings = get_settings()

    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/", params={"short": True}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 2

    if content[0]["uid"] == db_provider_with_single_project.uid:
        resp_prov = content[0]
        resp_prov2 = content[1]
    else:
        resp_prov = content[1]
        resp_prov2 = content[0]

    validate_read_short_provider_attrs(
        obj_out=ProviderReadShort(**resp_prov),
        db_item=db_provider_with_single_project,
    )
    validate_read_short_provider_attrs(
        obj_out=ProviderReadShort(**resp_prov2),
        db_item=db_provider_with_multiple_projects,
    )


def test_read_provider(
    db_provider_with_single_project: Provider, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read a provider."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/{db_provider_with_single_project.uid}"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_provider_attrs(
        obj_out=ProviderRead(**content),
        db_item=db_provider_with_single_project,
    )


def test_read_provider_with_conn(
    db_provider_with_single_project: Provider, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read a provider with its relationships."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/{db_provider_with_single_project.uid}",
        params={"with_conn": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_extended_provider_attrs(
        obj_out=ProviderReadExtended(**content),
        db_item=db_provider_with_single_project,
    )


def test_read_provider_short(
    db_provider_with_single_project: Provider, api_client_read_only: TestClient
) -> None:
    """Execute GET operations to read the shrunk version of a provider."""
    settings = get_settings()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/{db_provider_with_single_project.uid}",
        params={"short": True},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    validate_read_short_provider_attrs(
        obj_out=ProviderReadShort(**content),
        db_item=db_provider_with_single_project,
    )


def test_read_not_existing_provider(api_client_read_only: TestClient) -> None:
    """Execute GET operations to try to read a not existing provider."""
    settings = get_settings()
    item_uuid = uuid4()
    response = api_client_read_only.get(
        f"{settings.API_V1_STR}/providers/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"Provider '{item_uuid}' not found"


def test_patch_provider(
    db_provider_with_single_project: Provider, api_client_read_write: TestClient
) -> None:
    """Execute PATCH operations to update a provider."""
    settings = get_settings()
    data = create_random_provider_patch()

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/providers/{db_provider_with_single_project.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    for k, v in data.dict().items():
        assert content[k] == v


def test_patch_provider_no_edit(
    db_provider: Provider, api_client_read_write: TestClient
) -> None:
    """Execute PATCH operations to update a provider.

    Nothing changes.
    """
    settings = get_settings()
    data = create_random_provider_patch(default=True)

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/providers/{db_provider.uid}",
        json=json.loads(data.json(exclude_unset=True)),
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED


def test_patch_not_existing_provider(api_client_read_write: TestClient) -> None:
    """Execute PATCH operations to try to update a not existing provider."""
    settings = get_settings()
    item_uuid = uuid4()
    data = create_random_provider_patch()

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/providers/{item_uuid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"Provider '{item_uuid}' not found"


def test_patch_provider_with_duplicated_name(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_write: TestClient,
) -> None:
    """Execute PATCH operations to try to assign an already existing name to a provider
    with the same type.
    """
    settings = get_settings()
    data = create_random_provider_patch()
    data.name = db_provider_with_single_project.name
    data.type = db_provider_with_single_project.type

    response = api_client_read_write.patch(
        f"{settings.API_V1_STR}/providers/{db_provider_with_multiple_projects.uid}",
        json=json.loads(data.json()),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert (
        content["detail"] == f"{data.type.capitalize()} provider with "
        f"name '{data.name}' already registered"
    )


# TODO Add tests raising 422


def test_delete_provider(
    db_provider_with_single_project: Provider,
    db_provider_with_multiple_projects: Provider,
    api_client_read_write: TestClient,
) -> None:
    """Execute DELETE to remove a public provider."""
    settings = get_settings()
    response = api_client_read_write.delete(
        f"{settings.API_V1_STR}/providers/{db_provider_with_single_project.uid}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_not_existing_provider(api_client_read_write: TestClient) -> None:
    """Execute DELETE operations to try to delete a not existing provider."""
    settings = get_settings()
    item_uuid = uuid4()
    response = api_client_read_write.delete(
        f"{settings.API_V1_STR}/providers/{item_uuid}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == f"Provider '{item_uuid}' not found"
