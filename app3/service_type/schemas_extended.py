from pydantic import validator
from typing import List

from ..quota_type.schemas import QuotaType, QuotaTypeCreate
from ..service_type.schemas import ServiceType, ServiceTypeCreate
from ..validators import get_all_nodes_from_rel


class ServiceTypeCreateExtended(ServiceTypeCreate):
    """Service Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT or POST request.

    Attributes:
        description (str): Brief description.
        name (str): type unique name.
        quota_types (list of QuotaTypeCreate): supported quota types for
            this kind of service.
    """

    quota_types: List[QuotaTypeCreate]


class ServiceTypeExtended(ServiceType):
    """Service class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        name (str): type unique name.
        quota_types (list of QuotaType): supported quota types for
            this kind of service.
    """

    quota_types: List[QuotaType]

    _get_all_quota_types = validator(
        "quota_types", pre=True, allow_reuse=True
    )(get_all_nodes_from_rel)
