from typing import Literal, Optional

from pydantic import Field, validator

from app.models import BaseNode, BaseNodeCreate, BaseNodeRead
from app.query import create_query_model
from app.quota.enum import QuotaType


class QuotaBase(BaseNode):
    """Model with Quota basic attributes."""

    type: QuotaType = Field(description="Quota type.")
    per_user: bool = Field(default=False, description="Quota to apply for each user")


class BlockStorageQuotaBase(QuotaBase):
    """Model derived from ServiceBase to inherit attributes common to all services.

    It adds the basic attributes for BlockStorage services.

    Validation: type value is exactly QuotaType.openstack_nova.
    """

    type: QuotaType = Field(
        default=QuotaType.BLOCK_STORAGE, description="Block storage type"
    )
    gigabytes: Optional[int] = Field(default=None, ge=-1, description="")
    per_volume_gigabytes: Optional[int] = Field(default=None, ge=-1, description="")
    volumes: Optional[int] = Field(default=None, ge=-1, description="")

    @validator("type", check_fields=False)
    def check_type(cls, v) -> Literal[QuotaType.BLOCK_STORAGE]:
        if v != QuotaType.BLOCK_STORAGE:
            raise ValueError(f"Not valid type: {v}")
        return v


class BlockStorageQuotaCreate(BaseNodeCreate, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaUpdate(BaseNodeCreate, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaRead(BaseNodeRead, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaReadPublic(BaseNodeRead, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaReadShort(BaseNodeRead, BlockStorageQuotaBase):
    pass


BlockStorageQuotaQuery = create_query_model(
    "BlockStorageQuotaQuery", BlockStorageQuotaBase
)


class ComputeQuotaBase(QuotaBase):
    """Model derived from ServiceBase to inherit attributes common to all services.

    It adds the basic attributes for Compute services.

    Validation: type value is exactly QuotaType.openstack_nova.
    """

    type: QuotaType = Field(default=QuotaType.COMPUTE, description="Compute type")
    cores: Optional[int] = Field(default=None, ge=0, description="")
    instances: Optional[int] = Field(default=None, ge=0, description="")
    ram: Optional[int] = Field(default=None, ge=0, description="")

    @validator("type", check_fields=False)
    def check_type(cls, v) -> Literal[QuotaType.COMPUTE]:
        if v != QuotaType.COMPUTE:
            raise ValueError(f"Not valid type: {v}")
        return v


class ComputeQuotaCreate(BaseNodeCreate, ComputeQuotaBase):
    pass


class ComputeQuotaUpdate(BaseNodeCreate, ComputeQuotaBase):
    pass


class ComputeQuotaRead(BaseNodeRead, ComputeQuotaBase):
    pass


class ComputeQuotaReadPublic(BaseNodeRead, ComputeQuotaBase):
    pass


class ComputeQuotaReadShort(BaseNodeRead, ComputeQuotaBase):
    pass


ComputeQuotaQuery = create_query_model("ComputeQuotaQuery", ComputeQuotaBase)


class NetworkQuotaBase(QuotaBase):
    """Model derived from ServiceBase to inherit attributes common to all services.

    It adds the basic attributes for Network services.

    Validation: type value is exactly QuotaType.openstack_nova.
    """

    type: QuotaType = Field(default=QuotaType.NETWORK, description="Network type")
    public_ips: Optional[int] = Field(
        default=None,
        ge=-1,
        description="The number of floating IP addresses allowed for each project.",
    )
    networks: Optional[int] = Field(
        default=None,
        ge=-1,
        description="The number of networks allowed for each project.",
    )
    ports: Optional[int] = Field(
        default=None, ge=-1, description="The number of ports allowed for each project."
    )
    security_groups: Optional[int] = Field(
        default=None,
        ge=-1,
        description="The number of security groups allowed for each project.",
    )
    security_group_rules: Optional[int] = Field(
        default=None,
        ge=-1,
        description="The number of security group rules allowed for each",
    )

    @validator("type", check_fields=False)
    def check_type(cls, v) -> Literal[QuotaType.NETWORK]:
        if v != QuotaType.NETWORK:
            raise ValueError(f"Not valid type: {v}")
        return v


class NetworkQuotaCreate(BaseNodeCreate, NetworkQuotaBase):
    pass


class NetworkQuotaUpdate(BaseNodeCreate, NetworkQuotaBase):
    pass


class NetworkQuotaRead(BaseNodeRead, NetworkQuotaBase):
    pass


class NetworkQuotaReadPublic(BaseNodeRead, NetworkQuotaBase):
    pass


class NetworkQuotaReadShort(BaseNodeRead, NetworkQuotaBase):
    pass


NetworkQuotaQuery = create_query_model("NetworkQuotaQuery", NetworkQuotaBase)
