"""Image specific fixtures."""
from typing import Any, Dict

from pytest_cases import fixture, fixture_union, parametrize

from app.image.crud import image_mng
from app.image.models import Image
from app.provider.models import Provider
from app.provider.schemas_extended import ImageCreateExtended
from app.region.models import Region
from app.service.models import ComputeService

relationships_num = [0, 1, 2]


@fixture
@parametrize(owned_projects=relationships_num)
def db_image_simple(
    owned_projects: int,
    image_create_mandatory_data: Dict[str, Any],
    db_compute_service_with_projects: ComputeService,
) -> Image:
    """Fixture with standard DB Image.

    The image can be public or private based on the number of allowed projects.
    0 - Public. 1 or 2 - Private.
    """
    db_region: Region = db_compute_service_with_projects.region.single()
    db_provider: Provider = db_region.provider.single()
    projects = [i.uuid for i in db_provider.projects]
    item = ImageCreateExtended(
        **image_create_mandatory_data,
        is_public=owned_projects == 0,
        projects=projects[:owned_projects],
    )
    return image_mng.create(
        obj_in=item,
        service=db_compute_service_with_projects,
        projects=db_provider.projects,
    )


@fixture
def db_shared_image(
    image_create_mandatory_data: Dict[str, Any],
    db_region_with_compute_services: Region,
) -> Image:
    """Image shared by multiple services."""
    item = ImageCreateExtended(**image_create_mandatory_data)
    for db_service in db_region_with_compute_services.services:
        db_item = image_mng.create(obj_in=item, service=db_service)
    assert len(db_item.services) > 1
    return db_item


db_image = fixture_union(
    "db_image", (db_image_simple, db_shared_image), idstyle="explicit"
)
