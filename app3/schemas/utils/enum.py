from enum import Enum


class ServiceType(Enum):
    """Possible IaaS services types"""

    open_stack_nova: str = "org.openstack.nova"
    mesos: str = "eu.indigo-datacloud.mesos"
    chronos: str = "eu.indigo-datacloud.chronos"
    marathon: str = "eu.indigo-datacloud.marathon"
    kubernetes: str = "eu.deep.kubernetes"
    rucio: str = "eu.egi.storage-element"
    onedata: str = "eu.egi.cloud.storage-management.oneprovider"


class ImageOS(Enum):
    """Possible operating systems types"""

    Linux: str = "Linux"
    Windows: str = "Windows"
    MacOS: str = "MacOS"


class QuotaTypeBandwidth(Enum):
    """Possibile Quota types with bandwidth measurement unit"""

    upload_bandwidth: str = "Upload Bandwidth"
    download_bandwidth: str = "Download Bandwidth"


class QuotaTypeCount(Enum):
    """Possibile Quota types with no measurement unit"""

    num_cpus: str = "Num CPUs"
    public_ip: str = "Public IPs"


class QuotaTypeFrequency(Enum):
    """Possibile Quota types with frequency measurement unit"""

    cpu_frequency: str = "CPU frequency"


class QuotaTypeMoney(Enum):
    """Possibile Quota types with money measurement unit"""

    cost: str = "Cost"


class QuotaTypeSize(Enum):
    """Possibile Quota types with space measurement unit"""

    mem_size: str = "RAM Memory Size"
    disk_size: str = "Disk Size"
    upload_aggregated: str = "Upload Aggregated"
    download_aggregated: str = "Download Aggregated"


class QuotaTypeTime(Enum):
    """Possibile Quota types with time measurement unit"""

    computing_time: str = "Compute Time"


class QuotaUnit(Enum):
    """Possibile Quota units"""

    bandwidth = "Mbps"
    freq = "Hz"
    money = "€"
    size = "MB"
    time = "h"
