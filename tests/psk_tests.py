from io import BytesIO
from pathlib import Path
import warnings

from pytest import approx
from psk_psa_py.psk.reader import read_psk, read_psk_from_file
from psk_psa_py.psk.writer import write_psk
from psk_psa_py.psk.data import Psk, PskSectionName
from psk_psa_py.shared.data import Section, Vector3, PsxBone


def _assert_psk_round_trip_data_is_unchanged(path: Path):
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


class TestPsk:
    
    def test_import_export_round_trip(self):
        """
        Ensures that all the data survives a round-trip from being read and written out again.
        """

        from glob import glob

        test_data_directory = './tests/data/psk'
        count = 0
        for filename in glob('*.psk', root_dir=test_data_directory):
            path = Path(test_data_directory) / filename
            path = path.resolve()
            _assert_psk_round_trip_data_is_unchanged(path)
            count += 1
        
        assert count > 0

    def test_extended_format(self):
        psk = read_psk_from_file('./tests/data/psk/CS_Sarge_S0_Skelmesh.pskx')
        assert len(psk.bones) == 266
        assert len(psk.extra_uvs) == 1
        assert psk.has_extra_uvs
        assert len(psk.faces) == 50807
        assert len(psk.vertex_colors) == 74280


    def test_sort_and_normalize_weights(self):
        """
        Test the sort_and_normalize_weights method with various weight scenarios.
        """
        psk = Psk()
        
        # Test case 1: Weights for multiple points, unsorted, sum != 1.0
        psk.weights = [
            Psk.Weight(weight=0.6, point_index=1, bone_index=0),
            Psk.Weight(weight=0.2, point_index=0, bone_index=0),
            Psk.Weight(weight=0.4, point_index=1, bone_index=1),
            Psk.Weight(weight=0.3, point_index=0, bone_index=1),
        ]
        
        psk.sort_and_normalize_weights()
        
        # Weights should be sorted by point_index
        assert psk.weights[0].point_index == 0
        assert psk.weights[1].point_index == 0
        assert psk.weights[2].point_index == 1
        assert psk.weights[3].point_index == 1
        
        # Weights for point 0 should be normalized (sum was 0.5, so divide by 0.5)
        assert approx(psk.weights[0].weight, abs=1e-6) == 0.4  # 0.2 / 0.5
        assert approx(psk.weights[1].weight, abs=1e-6) == 0.6  # 0.3 / 0.5
        
        # Weights for point 1 should be normalized (sum was 1.0, so divide by 1.0)
        assert approx(psk.weights[2].weight, abs=1e-6) == 0.6  # 0.6 / 1.0
        assert approx(psk.weights[3].weight, abs=1e-6) == 0.4  # 0.4 / 1.0


    def test_sort_and_normalize_weights_zero_sum(self):
        """
        Test sort_and_normalize_weights when weight sum is zero (should not divide by zero).
        """
        psk = Psk()
        
        psk.weights = [
            Psk.Weight(weight=0.0, point_index=0, bone_index=0),
            Psk.Weight(weight=0.0, point_index=0, bone_index=1),
        ]
        
        # Should not raise an error even with zero sum
        psk.sort_and_normalize_weights()
        
        # Weights should remain zero (not divided by zero)
        assert psk.weights[0].weight == 0.0
        assert psk.weights[1].weight == 0.0


    def test_sort_and_normalize_weights_single_point(self):
        """
        Test sort_and_normalize_weights with single weight per point.
        """
        psk = Psk()
        
        psk.weights = [
            Psk.Weight(weight=2.5, point_index=0, bone_index=0),
            Psk.Weight(weight=0.5, point_index=1, bone_index=0),
        ]
        
        psk.sort_and_normalize_weights()
        
        # Each weight should be normalized to 1.0 (single weight per point)
        assert approx(psk.weights[0].weight, abs=1e-6) == 1.0
        assert approx(psk.weights[1].weight, abs=1e-6) == 1.0


    def test_unhandled_section(self):
        """
        Test that unknown sections in PSK files generate warnings and are skipped.
        """
        # Create a synthetic PSK file with minimal valid structure plus an unknown section
        fp = BytesIO()
        
        # Write ACTRHEAD section (header)
        section = Section()
        section.name = PskSectionName.ACTRHEAD
        fp.write(section)
        
        # Write a minimal PNTS0000 section (points)
        section = Section()
        section.name = PskSectionName.PNTS0000
        section.data_size = 12
        section.data_count = 1
        fp.write(section)
        fp.write(Vector3())
        
        # Write an unknown section
        section = Section()
        section.name = b'UNKNOWN1234567890123'
        section.data_size = 4
        section.data_count = 2
        fp.write(section)
        fp.write(b'\x00' * 8)
        
        # Write REFSKELT section (bones)
        section = Section()
        section.name = PskSectionName.REFSKELT
        section.data_size = 120
        section.data_count = 1
        fp.write(section)
        fp.write(PsxBone())
        
        # Read the PSK and capture warnings
        fp.seek(0)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            psk = read_psk(fp)
            
            # Should have warned about the unknown section
            assert len(w) == 1
            assert "Unrecognized section" in str(w[0].message)
        
        # The PSK should still have read the valid sections
        assert len(psk.points) == 1
        assert len(psk.bones) == 1