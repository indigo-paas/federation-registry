from typing import List, Union

from app.auth_method.schemas import AuthMethodCreate
from app.identity_provider.models import IdentityProvider
from app.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderReadShort,
    IdentityProviderUpdate,
)
from app.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from app.provider.schemas_extended import IdentityProviderCreateExtended
from tests.utils.user_group import (
    create_random_user_group,
    validate_create_user_group_attrs,
)
from tests.utils.utils import random_lower_string, random_url


def create_random_identity_provider(
    *, default: bool = False, projects: List[str]
) -> IdentityProviderCreateExtended:
    endpoint = random_url()
    group_claim = random_lower_string()
    relationship = random_relationship()
    user_groups = []
    for p in projects:
        user_groups.append(create_random_user_group(project=p))
    kwargs = {}
    if not default:
        kwargs = {"description": random_lower_string()}
    return IdentityProviderCreateExtended(
        endpoint=endpoint,
        group_claim=group_claim,
        relationship=relationship,
        user_groups=user_groups,
        **kwargs,
    )


def create_random_identity_provider_patch(
    *, default: bool = False
) -> IdentityProviderUpdate:
    if default:
        return IdentityProviderUpdate()
    endpoint = random_url()
    group_claim = random_lower_string()
    kwargs = {"description": random_lower_string()}
    return IdentityProviderUpdate(endpoint=endpoint, group_claim=group_claim, **kwargs)


def random_relationship() -> AuthMethodCreate:
    idp_name = random_lower_string()
    protocol = random_lower_string()
    return AuthMethodCreate(idp_name=idp_name, protocol=protocol)


def validate_public_attrs(
    *, obj_in: IdentityProviderBase, db_item: IdentityProvider
) -> None:
    assert db_item.description == obj_in.description
    assert db_item.endpoint == obj_in.endpoint
    assert db_item.group_claim == obj_in.group_claim


def validate_attrs(*, obj_in: IdentityProviderBase, db_item: IdentityProvider) -> None:
    validate_public_attrs(obj_in=obj_in, db_item=db_item)


def validate_rels(
    *,
    obj_out: Union[IdentityProviderReadExtended, IdentityProviderReadExtendedPublic],
    db_item: IdentityProvider,
) -> None:
    assert len(db_item.providers) == len(obj_out.providers)
    for db_prov, prov_out in zip(
        sorted(db_item.providers, key=lambda x: x.uid),
        sorted(obj_out.providers, key=lambda x: x.uid),
    ):
        assert db_prov.uid == prov_out.uid
    assert len(db_item.user_groups) == len(obj_out.user_groups)
    for db_user, user_out in zip(
        sorted(db_item.user_groups, key=lambda x: x.uid),
        sorted(obj_out.user_groups, key=lambda x: x.uid),
    ):
        assert db_user.uid == user_out.uid


def validate_create_identity_provider_attrs(
    *, obj_in: IdentityProviderCreateExtended, db_item: IdentityProvider
) -> None:
    validate_attrs(obj_in=obj_in, db_item=db_item)
    for p in db_item.providers:
        auth_data = db_item.providers.relationship(p)
        assert auth_data
        assert obj_in.relationship
        assert auth_data.protocol == obj_in.relationship.protocol
        assert auth_data.idp_name == obj_in.relationship.idp_name
    assert len(db_item.user_groups) == len(obj_in.user_groups)
    for db_user, user_in in zip(
        sorted(db_item.user_groups, key=lambda x: x.name),
        sorted(obj_in.user_groups, key=lambda x: x.name),
    ):
        validate_create_user_group_attrs(obj_in=user_in, db_item=db_user)


def validate_read_identity_provider_attrs(
    *, obj_out: IdentityProviderRead, db_item: IdentityProvider
) -> None:
    assert db_item.uid == obj_out.uid
    validate_attrs(obj_in=obj_out, db_item=db_item)


def validate_read_short_identity_provider_attrs(
    *, obj_out: IdentityProviderReadShort, db_item: IdentityProvider
) -> None:
    assert db_item.uid == obj_out.uid
    validate_attrs(obj_in=obj_out, db_item=db_item)


def validate_read_public_identity_provider_attrs(
    *, obj_out: IdentityProviderReadPublic, db_item: IdentityProvider
) -> None:
    assert db_item.uid == obj_out.uid
    validate_public_attrs(obj_in=obj_out, db_item=db_item)


def validate_read_extended_identity_provider_attrs(
    *, obj_out: IdentityProviderReadExtended, db_item: IdentityProvider
) -> None:
    assert db_item.uid == obj_out.uid
    validate_attrs(obj_in=obj_out, db_item=db_item)
    validate_rels(obj_out=obj_out, db_item=db_item)


def validate_read_extended_public_identity_provider_attrs(
    *, obj_out: IdentityProviderReadExtendedPublic, db_item: IdentityProvider
) -> None:
    assert db_item.uid == obj_out.uid
    validate_public_attrs(obj_in=obj_out, db_item=db_item)
    validate_rels(obj_out=obj_out, db_item=db_item)
