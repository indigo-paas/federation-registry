from fastapi import APIRouter

from app.config import get_settings
from app.flavor.api.v1.endpoints import router as flavor_router_v1
from app.identity_provider.api.v1.endpoints import (
    router as identity_provider_router_v1,
)
from app.image.api.v1.endpoints import router as image_router_v1
from app.location.api.v1.endpoints import router as location_router_v1
from app.network.api.v1.endpoints import router as network_router_v1
from app.project.api.v1.endpoints import router as project_router_v1
from app.provider.api.v1.endpoints import router as provider_router_v1
from app.quota.api.v1.endpoints import (
    bs_router as block_storage_quota_router_v1,
)
from app.quota.api.v1.endpoints import c_router as compute_quota_router_v1
from app.quota.api.v1.endpoints import n_router as network_quota_router_v1
from app.region.api.v1.endpoints import router as region_router_v1
from app.service.api.v1.endpoints import (
    bs_router as block_storage_service_router_v1,
)
from app.service.api.v1.endpoints import c_router as compute_service_router_v1
from app.service.api.v1.endpoints import i_router as identity_service_router_v1
from app.service.api.v1.endpoints import n_router as network_service_router_v1
from app.sla.api.v1.endpoints import router as sla_router_v1
from app.user_group.api.v1.endpoints import router as user_group_router_v1

settings = get_settings()

router_v1 = APIRouter()
router_v1.include_router(flavor_router_v1)
router_v1.include_router(identity_provider_router_v1)
router_v1.include_router(image_router_v1)
router_v1.include_router(location_router_v1)
router_v1.include_router(network_router_v1)
router_v1.include_router(project_router_v1)
router_v1.include_router(provider_router_v1)
router_v1.include_router(block_storage_quota_router_v1)
router_v1.include_router(compute_quota_router_v1)
router_v1.include_router(network_quota_router_v1)
router_v1.include_router(block_storage_service_router_v1)
router_v1.include_router(compute_service_router_v1)
router_v1.include_router(identity_service_router_v1)
router_v1.include_router(network_service_router_v1)
router_v1.include_router(sla_router_v1)
router_v1.include_router(user_group_router_v1)
router_v1.include_router(region_router_v1)
