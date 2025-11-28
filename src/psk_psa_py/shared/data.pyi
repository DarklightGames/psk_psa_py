from ctypes import Structure
from typing import Tuple


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
