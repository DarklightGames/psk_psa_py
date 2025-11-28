from io import BufferedReader, BufferedWriter, BytesIO
from pathlib import Path
import pytest
from psk_psa_py.psk.reader import read_psk, read_psk_from_file
from psk_psa_py.psk.writer import write_psk
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@pytest.fixture(autouse=True)
def run_before_and_after_Tests(tmpdir):
    pass


def assert_psk_round_trip_data_is_unchanged(path: Path):
    input = read_psk_from_file(str(path))
    
    fp = BytesIO()

    write_psk(input, fp, is_extended_format=True)
    fp.seek(0)

    output = read_psk(fp)

    # Points
    assert len(input.points) == len(output.points)
    for i, (p1, p2) in enumerate(zip(input.points, output.points)):
        assert p1 == p2
    
    # Wedges
    assert len(input.wedges) == len(output.wedges)
    for i, (w1, w2) in enumerate(zip(input.wedges, output.wedges)):
        assert w1.material_index == w2.material_index
        assert w1.point_index == w2.point_index
        assert w1.u == w2.u
        assert w1.v == w2.v

    # Faces
    for i, (f1, f2) in enumerate(zip(input.faces, output.faces)):
        assert f1.aux_material_index == f2.aux_material_index
        assert f1.material_index == f2.material_index
        assert f1.smoothing_groups == f2.smoothing_groups
        assert tuple(f1.wedge_indices) == tuple(f2.wedge_indices) # TODO: comparing ctype backed arrays doesn't work.
    
    # Materials
    assert len(input.materials) == len(output.materials)
    for i, (m1, m2) in enumerate(zip(input.materials, output.materials)):
        assert m1.aux_flags == m2.aux_flags
        assert m1.aux_material == m2.aux_material
        assert m1.lod_bias == m2.lod_bias
        assert m1.lod_style == m2.lod_style
        assert m1.name == m2.name
        assert m1.poly_flags == m2.poly_flags
        assert m1.texture_index == m2.texture_index

    # Bones
    assert len(input.bones) == len(output.bones)
    for i, (b1, b2) in enumerate(zip(input.bones, output.bones)):
        assert b1.children_count == b2.children_count
        assert b1.flags == b2.flags
        assert b1.length == b2.length
        assert b1.name == b2.name
        assert b1.parent_index == b2.parent_index

    # Weights
    assert len(input.weights) == len(output.weights)
    for i, (w1, w2) in enumerate(zip(input.weights, output.weights)):
        assert w1.bone_index == w2.bone_index, "Weight {i} has mismatched bone index"
        assert w1.point_index == w2.point_index, "Weight {i} has mismatched point index"
        assert w1.weight == w2.weight, "Weight {i} has mismatched weight"
    
    # Extra UVs
    assert len(input.extra_uvs) == len(output.extra_uvs)
    for i, (u1, u2) in enumerate(zip(input.extra_uvs, output.extra_uvs)):
        assert u1 == u2

    # Vertex Colors
    assert len(input.vertex_colors) == len(output.vertex_colors)
    for i, (m1, m2) in enumerate(zip(input.vertex_colors, output.vertex_colors)):
        assert m1 == m2

    # Vertex Normals
    assert len(input.vertex_normals) == len(output.vertex_normals)
    for i, (m1, m2) in enumerate(zip(input.vertex_normals, output.vertex_normals)):
        assert m1 == m2

    # Morph Infos
    assert len(input.morph_infos) == len(output.morph_infos)
    for i, (m1, m2) in enumerate(zip(input.morph_infos, output.morph_infos)):
        assert m1.name == m2.name
        assert m1.vertex_count == m2.vertex_count
    
    # Morph Data
    assert len(input.morph_data) == len(output.morph_data)
    for i, (m1, m2) in enumerate(zip(input.morph_data, output.morph_data)):
        assert m1.point_index == m2.point_index
        assert m1.position_delta == m2.position_delta
        assert m1.tangent_z_delta == m2.tangent_z_delta
    
    # Material References
    assert len(input.material_references) == len(output.material_references)
    for i, (m1, m2) in enumerate(zip(input.material_references, output.material_references)):
        assert m1 == m2

def test_psk_import_export_round_trip():
    """
    Ensures that all the data survives a round-trip from being read and written out again.
    """

    from glob import glob

    test_data_directory = './tests/data'
    for filename in glob('*.psk', root_dir=test_data_directory):
        logger.warning(filename)
        path = Path(test_data_directory) / filename
        path = path.resolve()
        assert_psk_round_trip_data_is_unchanged(path)
        
