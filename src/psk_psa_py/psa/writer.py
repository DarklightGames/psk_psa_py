from ctypes import Structure, sizeof
from typing import Optional, Type, Collection, BinaryIO

from .data import Psa
from ..shared.data import PsxBone, Section


def _write_section(fp, name: bytes, data_type: Optional[Type[Structure]] = None, data: Optional[Collection] = None):
    section = Section()
    section.name = name
    if data_type is not None and data is not None:
        section.data_size = sizeof(data_type)
        section.data_count = len(data)
    fp.write(section)
    if data is not None:
        for datum in data:
            fp.write(datum)


def write_psa(psa: Psa, fp: BinaryIO):
    _write_section(fp, b'ANIMHEAD')
    _write_section(fp, b'BONENAMES', PsxBone, psa.bones)
    _write_section(fp, b'ANIMINFO', Psa.Sequence, list(psa.sequences.values()))
    _write_section(fp, b'ANIMKEYS', Psa.Key, psa.keys)


def write_psa_to_file(psa: Psa, path: str):
    with open(path, 'wb') as fp:
        write_psa(psa, fp)


__all__ = [
    'write_psa',
    'write_psa_to_file'
]


def __dir__():
    return __all__
