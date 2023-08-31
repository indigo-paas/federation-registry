from typing import List, Optional, Union

from app.auth.dependencies import flaat
from app.auth_method.schemas import AuthMethodCreate
from app.flavor.api.dependencies import valid_flavor_name, valid_flavor_uuid
from app.flavor.crud import flavor
from app.flavor.schemas import FlavorCreate
from app.flavor.schemas_extended import FlavorReadExtended
from app.identity_provider.api.dependencies import valid_identity_provider_id
from app.identity_provider.models import IdentityProvider
from app.image.api.dependencies import valid_image_name, valid_image_uuid
from app.image.crud import image
from app.image.schemas import ImageCreate
from app.image.schemas_extended import ImageReadExtended
from app.location.api.dependencies import valid_location_id
from app.location.models import Location
from app.pagination import Pagination, paginate
from app.project.api.dependencies import valid_project_name, valid_project_uuid
from app.project.crud import project
from app.project.schemas import ProjectCreate
from app.project.schemas_extended import ProjectReadExtended
from app.provider.api.dependencies import (
    is_unique_provider,
    valid_flavor_list,
    valid_identity_provider_list,
    valid_image_list,
    valid_location,
    valid_project_list,
    valid_provider_id,
    valid_service_list,
    validate_new_provider_values,
)
from app.provider.crud import provider
from app.provider.models import Provider
from app.provider.schemas import ProviderQuery, ProviderUpdate
from app.provider.schemas_extended import ProviderCreateExtended, ProviderReadExtended
from app.query import CommonGetQuery
from app.service.api.dependencies import valid_service_endpoint
from app.service.crud import service
from app.service.schemas import (
    ChronosServiceCreate,
    KubernetesServiceCreate,
    MarathonServiceCreate,
    MesosServiceCreate,
    NovaServiceCreate,
    OneDataServiceCreate,
    RucioServiceCreate,
)
from app.service.schemas_extended import (
    ChronosServiceReadExtended,
    KubernetesServiceReadExtended,
    MarathonServiceReadExtended,
    MesosServiceReadExtended,
    NovaServiceReadExtended,
    OneDataServiceReadExtended,
    RucioServiceReadExtended,
)
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from neomodel import db

router = APIRouter(prefix="/providers", tags=["providers"])


@db.read_transaction
@router.get(
    "/",
    response_model=List[ProviderReadExtended],
    summary="Read all providers",
    description="Retrieve all providers stored in the database. \
        It is possible to filter on providers attributes and other \
        common query parameters.",
)
@flaat.is_authenticated()
def get_providers(
    request: Request,
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: ProviderQuery = Depends(),
):
    items = provider.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.write_transaction
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProviderReadExtended,
    dependencies=[
        Depends(is_unique_provider),
        Depends(valid_flavor_list),
        Depends(valid_identity_provider_list),
        Depends(valid_image_list),
        Depends(valid_location),
        Depends(valid_project_list),
        Depends(valid_service_list),
    ],
    summary="Create provider",
    description="Create a provider and its related entities: \
        flavors, identity providers, images, location, \
        projects and services. \
        At first validate new provider values checking there are \
        no other items with the given *name*. \
        Moreover check the received lists do not contain duplicates.",
)
@flaat.access_level("write")
def post_provider(request: Request, item: ProviderCreateExtended):
    return provider.create(obj_in=item, force=True)


@db.read_transaction
@router.get(
    "/{provider_uid}",
    response_model=ProviderReadExtended,
    summary="Read a specific provider",
    description="Retrieve a specific provider using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@flaat.is_authenticated()
def get_provider(request: Request, item: Provider = Depends(valid_provider_id)):
    return item


@db.write_transaction
@router.patch(
    "/{provider_uid}",
    response_model=Optional[ProviderReadExtended],
    dependencies=[Depends(validate_new_provider_values)],
    summary="Edit a specific provider",
    description="Update attribute values of a specific provider. \
        The target provider is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new provider values checking there are \
        no other items with the given *name*.",
)
@flaat.access_level("write")
def put_provider(
    request: Request,
    update_data: ProviderUpdate,
    response: Response,
    item: Provider = Depends(valid_provider_id),
):
    db_item = provider.update(db_obj=item, obj_in=update_data)
    if db_item is None:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@db.write_transaction
@router.delete(
    "/{provider_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific provider",
    description="Delete a specific provider using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related flavors, images, projects \
        and services.",
)
@flaat.access_level("write")
def delete_providers(request: Request, item: Provider = Depends(valid_provider_id)):
    if not provider.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


@db.write_transaction
@router.post(
    "/{provider_uid}/flavors/",
    response_model=FlavorReadExtended,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(valid_flavor_name), Depends(valid_flavor_uuid)],
    summary="Add new flavor to provider",
    description="Create a flavor and connect it to a \
        provider knowing it *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        At first validate new flavor values checking there are \
        no other items with the given *name* or *uuid*.",
)
@flaat.access_level("write")
def add_flavor_to_provider(
    request: Request,
    item: FlavorCreate,
    provider: Provider = Depends(valid_provider_id),
):
    return flavor.create(obj_in=item, provider=provider, force=True)


@db.write_transaction
@router.put(
    "/{provider_uid}/identity_providers/{identity_provider_uid}",
    response_model=ProviderReadExtended,
    summary="Connect provider to identity provider",
    description="Connect a provider to a specific identity \
        provider knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
@flaat.access_level("write")
def connect_provider_to_identity_providers(
    request: Request,
    data: AuthMethodCreate,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
):
    if item.identity_providers.is_connected(identity_provider):
        db_item = item.identity_providers.relationship(identity_provider)
        if all(
            [
                db_item.__getattribute__(k) == v
                for k, v in data.dict(exclude_unset=True).items()
            ]
        ):
            response.status_code = status.HTTP_304_NOT_MODIFIED
            return None
        item.identity_providers.disconnect(identity_provider)
    item.identity_providers.connect(identity_provider, data.dict())
    return item


@db.write_transaction
@router.delete(
    "/{provider_uid}/identity_providers/{identity_provider_uid}",
    response_model=ProviderReadExtended,
    summary="Disconnect provider from identity provider",
    description="Disconnect a provider from a specific identity \
        provider knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
@flaat.access_level("write")
def disconnect_provider_from_identity_providers(
    request: Request,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
):
    if not item.identity_providers.is_connected(identity_provider):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.identity_providers.disconnect(identity_provider)
    return item


@db.write_transaction
@router.post(
    "/{provider_uid}/images/",
    response_model=ImageReadExtended,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(valid_image_name), Depends(valid_image_uuid)],
    summary="Add new image to provider",
    description="Create a image and connect it to a \
        provider knowing it *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        At first validate new image values checking there are \
        no other items with the given *name* or *uuid*.",
)
@flaat.access_level("write")
def add_image_to_provider(
    request: Request,
    item: ImageCreate,
    provider: Provider = Depends(valid_provider_id),
):
    return image.create(obj_in=item, provider=provider, force=True)


@db.write_transaction
@router.put(
    "/{provider_uid}/locations/{location_uid}",
    response_model=ProviderReadExtended,
    summary="Connect provider to location",
    description="Connect a provider to a specific location \
        knowing their *uid*s. \
        If the provider already has a \
        current location and the new one is different, \
        the endpoint replaces it with the new one, otherwise \
        it leaves the entity unchanged and returns a \
        `not modified` message. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
@flaat.access_level("write")
def connect_provider_to_location(
    request: Request,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    location: Location = Depends(valid_location_id),
):
    if item.location.single() is None:
        item.location.connect(location)
    elif not item.location.is_connected(location):
        item.location.replace(location)
    else:
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    return item


@db.write_transaction
@router.delete(
    "/{provider_uid}/locations/{location_uid}",
    response_model=ProviderReadExtended,
    summary="Disconnect provider from location",
    description="Disconnect a provider from a specific location \
        knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
@flaat.access_level("write")
def disconnect_provider_from_location(
    request: Request,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    location: Location = Depends(valid_location_id),
):
    if not item.location.is_connected(location):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.location.disconnect(location)
    return item


@db.write_transaction
@router.post(
    "/{provider_uid}/projects/",
    response_model=ProjectReadExtended,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(valid_project_name), Depends(valid_project_uuid)],
    summary="Add new project to provider",
    description="Create a project and connect it to a \
        provider knowing it *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        At first validate new project values checking there are \
        no other items with the given *name* or *uuid*.",
)
@flaat.access_level("write")
def add_project_to_provider(
    request: Request,
    item: ProjectCreate,
    provider: Provider = Depends(valid_provider_id),
):
    return project.create(obj_in=item, provider=provider, force=True)


@db.write_transaction
@router.post(
    "/{provider_uid}/services/",
    response_model=Union[
        ChronosServiceReadExtended,
        KubernetesServiceReadExtended,
        MarathonServiceReadExtended,
        MesosServiceReadExtended,
        NovaServiceReadExtended,
        OneDataServiceReadExtended,
        RucioServiceReadExtended,
    ],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(valid_service_endpoint)],
    summary="Add new service to provider",
    description="Create a service and connect it to a \
        provider knowing it *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        At first validate new service values checking there are \
        no other items with the given *name* or *uuid*.",
)
@flaat.access_level("write")
def add_service_to_provider(
    request: Request,
    item: Union[
        ChronosServiceCreate,
        KubernetesServiceCreate,
        MarathonServiceCreate,
        MesosServiceCreate,
        NovaServiceCreate,
        OneDataServiceCreate,
        RucioServiceCreate,
    ],
    provider: Provider = Depends(valid_provider_id),
):
    return service.create(obj_in=item, provider=provider, force=True)
