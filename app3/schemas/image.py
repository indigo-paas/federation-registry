from enum import Enum
from pydantic import BaseModel


class ImageOS(Enum):
    """Possible Operating system types"""

    Linux: str = "Linux"
    Windows: str = "Windows"
    MacOS: str = "MacOS"


class ImageBase(BaseModel):
    """Image Base class.

    Class without id which is populated by the database.

    Attributes:
        name (str): Image name.
        os (str): Operating system type (Windows, Linux, Mac) # Ex type
        distribution (str): Distribution type (Ubuntu, CentOS...)
        version (str): Distribution version id
        architecture (str): OS architecture.
        cuda_support (bool): Enable support for CUDA.
        gpu_driver (bool): Enable support for GPU # TODO review comment/name.
        market_place (str): # TODO: What is it?
    """

    name: str
    os: ImageOS
    distribution: str
    version: str
    architecture: str
    market_place: str = ""
    description: str = ""
    cuda_support: bool = False
    gpu_driver: bool = False

    class Config:
        validate_assignment = True


class ImageCreate(ImageBase):
    """Image Base class.

    Class without id which is populated by the database.

    Attributes:
        name (str): Image name.
        os (str): Operating system type (Windows, Linux, Mac) # Ex type
        distribution (str): Distribution type (Ubuntu, CentOS...)
        version (str): Distribution version id
        architecture (str): OS architecture.
        cuda_support (bool): Enable support for CUDA.
        gpu_driver (bool): Enable support for GPU # TODO review comment/name.
        market_place (str): # TODO: What is it?
    """

    pass


class Image(ImageBase):
    """Image Base class.

    Class without id which is populated by the database.

    Attributes:
        id (int): Image unique ID.
        name (str): Image name.
        os (str): Operating system type (Windows, Linux, Mac) # Ex type
        distribution (str): Distribution type (Ubuntu, CentOS...)
        version (str): Distribution version id
        architecture (str): OS architecture.
        cuda_support (bool): Enable support for CUDA.
        gpu_driver (bool): Enable support for GPU # TODO review comment/name.
        market_place (str): # TODO: What is it?
    """

    uid: str

    class Config:
        orm_mode = True
