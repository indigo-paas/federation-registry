from typing import List

from app.crud import CRUDBase
from app.identity_provider.models import IdentityProvider
from app.project.models import Project
from app.project.schemas_extended import (
    UserGroupReadExtended,
    UserGroupReadExtendedPublic,
)
from app.provider.schemas_extended import UserGroupCreateExtended
from app.sla.crud import sla
from app.user_group.models import UserGroup
from app.user_group.schemas import (
    UserGroupCreate,
    UserGroupRead,
    UserGroupReadPublic,
    UserGroupReadShort,
    UserGroupUpdate,
)


class CRUDUserGroup(
    CRUDBase[
        UserGroup,
        UserGroupCreate,
        UserGroupUpdate,
        UserGroupRead,
        UserGroupReadPublic,
        UserGroupReadShort,
        UserGroupReadExtended,
        UserGroupReadExtendedPublic,
    ]
):
    """"""

    def create(
        self,
        *,
        obj_in: UserGroupCreateExtended,
        identity_provider: IdentityProvider,
        projects: List[Project]
    ) -> UserGroup:
        db_obj = identity_provider.user_groups.get_or_none(name=obj_in.name)
        if db_obj is None:
            db_obj = super().create(obj_in=obj_in)
            db_obj.identity_provider.connect(identity_provider)
        for item in obj_in.slas:
            item_projects = [str(i) for i in item.projects]
            db_projects = list(filter(lambda x: x.uuid in item_projects, projects))
            sla.create(obj_in=item, user_group=db_obj, projects=db_projects, force=True)
        return db_obj

    def remove(self, *, db_obj: UserGroup) -> bool:
        for item in db_obj.slas.all():
            sla.remove(db_obj=item)
        return super().remove(db_obj=db_obj)


user_group = CRUDUserGroup(
    model=UserGroup,
    create_schema=UserGroupCreate,
    read_schema=UserGroupRead,
    read_public_schema=UserGroupReadPublic,
    read_short_schema=UserGroupReadShort,
    read_extended_schema=UserGroupReadExtended,
    read_extended_public_schema=UserGroupReadExtendedPublic,
)
