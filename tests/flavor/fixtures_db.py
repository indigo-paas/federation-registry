"""Flavor specific fixtures."""
import pytest
from pytest_cases import fixture, fixture_union, parametrize

from app.flavor.crud import flavor_mng
from app.flavor.models import Flavor
from app.provider.models import Provider
from app.provider.schemas_extended import FlavorCreateExtended
from app.region.models import Region
from app.service.models import ComputeService
from tests.flavor.utils import random_flavor_required_attr


@fixture
@parametrize(owned_projects=[0, 1, 2])
def db_flavor_simple(
    owned_projects: int, db_compute_service_with_projects: ComputeService
) -> Flavor:
    """Fixture with standard DB Flavor.

    The flavor can be public or private based on the number of allowed projects.
    0 - Public. 1 or 2 - Private.
    """
    db_region: Region = db_compute_service_with_projects.region.single()
    db_provider: Provider = db_region.provider.single()
    projects = [i.uuid for i in db_provider.projects]
    item = FlavorCreateExtended(
        **random_flavor_required_attr(),
        is_public=owned_projects == 0,
        projects=projects[:owned_projects],
    )
    return flavor_mng.create(
        obj_in=item,
        service=db_compute_service_with_projects,
        projects=db_provider.projects,
    )


@fixture
def db_shared_flavor(db_region_with_compute_services: Region) -> Flavor:
    """Flavor shared by multiple services."""
    item = FlavorCreateExtended(**random_flavor_required_attr())
    if len(db_region_with_compute_services.services) == 1:
        pytest.skip("Case with only one service already considered.")
    for db_service in db_region_with_compute_services.services:
        db_item = flavor_mng.create(obj_in=item, service=db_service)
    assert len(db_item.services) > 1
    return db_item


db_flavor = fixture_union(
    "db_flavor", (db_flavor_simple, db_shared_flavor), idstyle="explicit"
)
