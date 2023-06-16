from typing import List, Optional
from .. import schemas, models


def create_location(item: schemas.LocationCreate) -> models.Location:
    return models.Location(**item.dict()).save()


def get_locations(
    skip: int = 0, limit: Optional[int] = None, sort: Optional[str] = None, **kwargs
) -> List[models.Location]:
    if kwargs:
        items = models.Location.nodes.filter(**kwargs).order_by(sort).all()
    else:
        items = models.Location.nodes.order_by(sort).all()
    if limit is None:
        return items[skip:]
    return items[skip : skip + limit]


def get_location(**kwargs) -> Optional[models.Location]:
    return models.Location.nodes.get_or_none(**kwargs)


def remove_location(item: models.Location) -> bool:
    return item.delete()


def update_location(
    old_item: models.Location, new_item: schemas.LocationUpdate
) -> Optional[models.Location]:
    for k, v in new_item.dict(exclude_unset=True).items():
        old_item.__setattr__(k, v)
    old_item.save()
    return old_item
