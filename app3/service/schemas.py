from pydantic import AnyUrl
from typing import Optional

from ..models import BaseNodeCreate, BaseNodeQuery, BaseNodeRead


class ServiceQuery(BaseNodeQuery):
    """Service Query Model class.

    Attributes:
        description (str | None): Brief description.
        endpoint (str | None): URL pointing to this service
    """

    endpoint: Optional[AnyUrl] = None


class ServiceCreate(BaseNodeCreate):
    """Service Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH, PUT or POST request.

    Attributes:
        description (str): Brief description.
        endpoint (str): URL pointing to this service
        type (ServiceTypePatch): Service type.
    """

    endpoint: AnyUrl


class Service(ServiceCreate, BaseNodeRead):
    """Service class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        endpoint (str): URL pointing to this service
        type (ServiceType): Service type.
    """