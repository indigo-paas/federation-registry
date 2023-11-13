from neomodel import (
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
)


class Service(StructuredNode):
    """Service supplied by a Provider on a specific Region.

    Common attributes to all service types.
    Any service is accessible through an endpoint, which is unique in the DB.

    TODO: function using cypher to retrieve IDPs?

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    endpoint = StringProperty(unique_index=True, required=True)
    type = StringProperty(required=True)
    name = StringProperty(required=True)

    region = RelationshipFrom("..region.models.Region", "SUPPLY", cardinality=One)


class BlockStorageService(Service):
    """Service managing Block Storage resources.

    A Block Storage Service, for each project, support a set of quotas managing the
    block storage resources.
    """

    quotas = RelationshipFrom(
        "..quota.models.BlockStorageQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class ComputeService(Service):
    """Service managing Compute resources.

    A Compute Service, for each project, support a set of quotas managing the block
    storage resources. A Compute Service provides public and private Flavors and Images.
    """

    flavors = RelationshipTo(
        "..flavor.models.Flavor",
        "AVAILABLE_VM_FLAVOR",
        cardinality=ZeroOrMore,
    )
    images = RelationshipTo(
        "..image.models.Image",
        "AVAILABLE_VM_IMAGE",
        cardinality=ZeroOrMore,
    )
    quotas = RelationshipFrom(
        "..quota.models.ComputeQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class IdentityService(Service):
    """Service managing user access to the Provider."""


class NetworkService(Service):
    """Service managing Network resources.

    A Network Service provides public and private Networks.
    """

    networks = RelationshipTo(
        "..network.models.Network",
        "AVAILABLE_NETWORK",
        cardinality=ZeroOrMore,
    )
    quotas = RelationshipFrom(
        "..quota.models.NetworkQuota", "APPLY_TO", cardinality=ZeroOrMore
    )
