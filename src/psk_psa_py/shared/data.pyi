from ctypes import Structure
from enum import Enum
from typing import Tuple


class PskSectionName(bytes, Enum):
    ACTRHEAD = b'ACTRHEAD'
    PNTS0000 = b'PNTS0000'
    VTXW0000 = b'VTXW0000'
    FACE0000 = b'FACE0000'
    MATT0000 = b'MATT0000'
    REFSKELT = b'REFSKELT'
    RAWWEIGHTS = b'RAWWEIGHTS'
    FACE3200 = b'FACE3200'
    VERTEXCOLOR = b'VERTEXCOLOR'
    VTXNORMS = b'VTXNORMS'
    MRPHINFO = b'MRPHINFO'
    MRPHDATA = b'MRPHDATA'

class PsaSectionName(bytes, Enum):
    ANIMHEAD = b'ANIMHEAD'
    BONENAMES = b'BONENAMES'
    ANIMINFO = b'ANIMINFO'
    ANIMKEYS = b'ANIMKEYS'


class StructureEq(Structure):
    pass


class Color(StructureEq):
    r: int
    g: int
    b: int
    a: int

    def normalized(self) -> Tuple:
        pass


class Vector2(StructureEq):
    x: float
    y: float


class Vector3(StructureEq):
    x: float
    y: float
    z: float

    @classmethod
    def zero(cls) -> Vector3:
        pass


class Quaternion(StructureEq):
    x: float
    y: float
    z: float
    w: float

    @classmethod
    def identity(cls) -> Quaternion:
        pass


class PsxBone(StructureEq):
    name: bytes
    flags: int
    children_count: int
    parent_index: int
    rotation: Quaternion
    location: Vector3
    length: float
    size: Vector3


class Section(StructureEq):
    name: bytes
    type_flags: int
    data_size: int
    data_count: int
