from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from app.location.crud import location
from app.location.models import Location
from app.location.schemas import LocationUpdate


def valid_location_id(location_uid: UUID4) -> Location:
    item = location.get(uid=str(location_uid).replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{location_uid}' not found",
        )
    return item


def validate_new_location_values(
    update_data: LocationUpdate, item: Location = Depends(valid_location_id)
) -> None:
    if update_data.name != item.name:
        db_item = location.get(name=update_data.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with name '{update_data.name}' already registered",
            )
