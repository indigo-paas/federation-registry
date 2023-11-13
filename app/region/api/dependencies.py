from typing import Union

from fastapi import Depends, HTTPException, status

from app.provider.api.dependencies import valid_provider_id
from app.provider.models import Provider
from app.region.crud import region
from app.region.models import Region
from app.region.schemas import RegionCreate, RegionUpdate


def valid_region_id(region_uid: str) -> Region:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        region_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Region: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = region.get(uid=region_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region '{region_uid}' not found",
        )
    return item


def is_unique_region(
    item: Union[RegionCreate, RegionUpdate],
    provider: Provider = Depends(valid_provider_id),
) -> None:
    """Check there are no other regions, belonging to the same provider, with the same
    name.

    Args:
    ----
        item (RegionCreate | RegionUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given name already exists.
    """
    db_item = provider.regions.get_or_none(name=item.name)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Region with name '{item.name}' already registered",
        )


def validate_new_region_values(
    update_data: RegionUpdate,
    item: Region = Depends(valid_region_id),
) -> None:
    """Check given data are valid ones. Check there are no other user groups, belonging
    to the same identity provider, with the same name.

    Args:
    ----
        update_data (RegionUpdate): new data.
        item (Region): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given name already exists.
    """
    if update_data.name != item.name:
        is_unique_region(item=update_data, provider=item.provider.single())
