from app.crud import CRUDBase
from app.project.models import Project
from app.project.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectReadPublic,
    ProjectReadShort,
    ProjectUpdate,
)
from app.project.schemas_extended import ProjectReadExtended, ProjectReadExtendedPublic
from app.provider.models import Provider
from app.quota.crud import quota
from app.sla.crud import sla


class CRUDProject(
    CRUDBase[
        Project,
        ProjectCreate,
        ProjectUpdate,
        ProjectRead,
        ProjectReadPublic,
        ProjectReadShort,
        ProjectReadExtended,
        ProjectReadExtendedPublic,
    ]
):
    """"""

    def create(self, *, obj_in: ProjectCreate, provider: Provider) -> Project:
        db_obj = super().create(obj_in=obj_in, force=True)
        db_obj.provider.connect(provider)
        return db_obj

    def remove(self, *, db_obj: Project) -> bool:
        for item in db_obj.quotas:
            quota.remove(db_obj=item)
        item = db_obj.sla.single()
        if item is not None:
            sla.remove(db_obj=item)
        return super().remove(db_obj=db_obj)


project = CRUDProject(
    model=Project,
    create_schema=ProjectCreate,
    read_schema=ProjectRead,
    read_public_schema=ProjectReadPublic,
    read_short_schema=ProjectReadShort,
    read_extended_schema=ProjectReadExtended,
    read_extended_public_schema=ProjectReadExtendedPublic,
)
