from typing import Union

from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from app.identity_provider.crud import identity_provider
from app.location.crud import location
from app.provider.crud import provider
from app.provider.models import Provider
from app.provider.schemas import ProviderUpdate
from app.provider.schemas_extended import (
    IdentityProviderCreateExtended,
    ProviderCreateExtended,
    RegionCreateExtended,
)
from app.service.api.dependencies import (
    valid_block_storage_service_endpoint,
    valid_compute_service_endpoint,
    valid_identity_service_endpoint,
    valid_network_service_endpoint,
)
from app.sla.crud import sla


def valid_provider_id(provider_uid: UUID4) -> Provider:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        provider_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Provider: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = provider.get(uid=str(provider_uid).replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_uid}' not found",
        )
    return item


def is_unique_provider(item: Union[ProviderCreateExtended, ProviderUpdate]) -> None:
    """Check there are no other providers with the same name.

    Args:
    ----
        item (ProviderCreateExtended | ProviderUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given name already exists.
    """
    db_item = provider.get(name=item.name)
    if db_item is not None:
        if db_item.type == item.type:
            msg = f"{db_item.type.capitalize()} provider with name "
            msg += f"'{item.name}' already registered"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )


def validate_new_provider_values(
    update_data: ProviderUpdate, item: Provider = Depends(valid_provider_id)
) -> None:
    """Check given data are valid ones. Check there are no other providers with the same
    name.

    Args:
    ----
        update_data (ProviderUpdate): new data.
        item (Provider): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given name already exists.
    """
    if update_data.name != item.name:
        is_unique_provider(update_data)


def valid_provider(item: ProviderCreateExtended) -> None:
    """Check provider does not already exists and validate identity providers and
    regions.
    """
    is_unique_provider(item)
    for idp in item.identity_providers:
        valid_identity_provider(idp)
    for region in item.regions:
        valid_region(region)


def valid_identity_provider(
    item: IdentityProviderCreateExtended,
) -> None:
    """Check there are no identity providers with the same endpoint, in the identity
    provider list of the received provider. Check that all items have a corresponding
    relationship Check that if there is another identity provider in the DB with the
    same endpoint, it matches the given attributes.

    Args:
    ----
        item (ProviderCreateExtended): provider data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: multiple items with identical name or uuid,
            or DB entity with given endpoint already exists but has
            different attributes.
    """
    db_item = identity_provider.get(endpoint=item.endpoint)
    if db_item is not None:
        data = item.dict(exclude={"relationship", "user_groups"}, exclude_unset=True)
        for k, v in data.items():
            if db_item.__getattribute__(k) != v:
                msg = f"Identity Provider '{item.endpoint}' already exists with "
                msg += f"different attributes. Received: {data}. Stored: {db_item}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    for group in item.user_groups:
        db_item = sla.get(doc_uuid=group.sla.doc_uuid)
        if db_item is not None:
            db_group = db_item.user_group.single()
            db_idp = db_group.identity_provider.single()
            if db_group.name != group.name or db_idp.endpoint != item.endpoint:
                msg = f"SLA {group.sla.doc_uuid} already used by another group"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def valid_region(item: RegionCreateExtended) -> None:
    """"""
    if item.location is not None:
        db_item = location.get(site=item.location.site)
        if db_item is not None:
            for k, v in item.location.dict(exclude_unset=True).items():
                if db_item.__getattribute__(k) != v:
                    msg = f"Location '{item.location.site}' already exists with "
                    msg += f"different attributes. Received: {item.location.dict()}. "
                    msg += f"Stored: {db_item}"
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=msg
                    )

    for service in item.block_storage_services:
        valid_block_storage_service_endpoint(service)
    for service in item.compute_services:
        valid_compute_service_endpoint(service)
    for service in item.identity_services:
        valid_identity_service_endpoint(service)
    for service in item.network_services:
        valid_network_service_endpoint(service)
