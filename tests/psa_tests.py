from io import BytesIO, StringIO
from pathlib import Path
import sys
import tempfile
import os
from psk_psa_py.psa.config import read_psa_config
from psk_psa_py.psa.reader import PsaReader
from psk_psa_py.psa.writer import write_psa
from psk_psa_py.shared.data import Section, PsxBone
from psk_psa_py.psa.data import PsaSectionName


def _assert_psa_round_trip_data_is_unchanged(path: Path):
    input_reader = PsaReader(path)

    input = input_reader.psa
    
    fp = BytesIO()

    write_psa(input, fp)
    fp.seek(0)

    output_reader = PsaReader(path)
    output = output_reader.psa

    # Bones
    assert len(input.bones) == len(output.bones)
    for b1, b2 in zip(input.bones, output.bones):
        assert b1.children_count == b2.children_count
        assert b1.flags == b2.flags
        assert b1.length == b2.length
        assert b1.name == b2.name
        assert b1.parent_index == b2.parent_index
    
    # Sequences
    assert len(input.sequences) == len(output.sequences)
    for (k1, s1), (k2, s2) in zip(input.sequences.items(), output.sequences.items()):
        assert k1 == k2
        assert s1.bone_count == s2.bone_count
        assert s1.compression_style == s2.compression_style
        assert s1.name == s2.name
        assert s1.group == s2.group
        assert s1.root_include == s2.root_include
        assert s1.key_quotum == s2.key_quotum
        assert s1.key_reduction == s2.key_reduction
        assert s1.track_time == s2.track_time
        assert s1.start_bone == s2.start_bone
        assert s1.frame_start_index == s2.frame_start_index
        assert s1.frame_count == s2.frame_count

        # Keys
        input_keys = input_reader.read_sequence_keys(k1)
        output_keys = output_reader.read_sequence_keys(k2)

        # Matrix
        input_data_matrix = input_reader.read_sequence_data_matrix(k1)
        output_data_matrix = output_reader.read_sequence_data_matrix(k2)

        assert (input_data_matrix == output_data_matrix).all()

        for k1, k2 in zip(input_keys, output_keys):
            assert k1.location == k2.location
            assert k1.rotation == k2.rotation
            assert k1.time == k2.time

        assert len(input_keys) == len(output_keys)
    

class TestPsa:
    """
    PSA file tests.
    """

    def test_round_trip_all_files(self):
        """
        Ensures that all the data survives a round-trip from being read and written out again.
        """
        from glob import glob

        test_data_directory = './tests/data/psa'
        for filename in glob('*.psa', root_dir=test_data_directory):
            path = Path(test_data_directory) / filename
            path = path.resolve()
            _assert_psa_round_trip_data_is_unchanged(path)


    def test_config_read(self):
        psa_reader = PsaReader('./tests/data/psa/Carlos_StrafeLF90_2.psa')
        psa_sequence_names = list(psa_reader.sequences.keys())

        config_path = './tests/data/psa/Carlos_StrafeLF90_2.config'
        config = read_psa_config(psa_sequence_names, config_path)

        print(config)


    def test_unhandled_section(self):
        """
        Test that unknown sections in PSA files are skipped with a print message.
        """
        # Create a synthetic PSA file with minimal valid structure plus an unknown section
        fp = BytesIO()
        
        # Write ANIMHEAD section
        section = Section()
        section.name = PsaSectionName.ANIMHEAD
        fp.write(section)
        
        # Write BONENAMES section
        section = Section()
        section.name = PsaSectionName.BONENAMES
        section.data_size = 120
        section.data_count = 1
        fp.write(section)
        fp.write(PsxBone())

        unknown_section_name = b'UNKNOWN9999'
        
        # Write an unknown section
        section = Section()
        section.name = unknown_section_name
        section.data_size = 4
        section.data_count = 3
        fp.write(section)
        fp.write(b'\xFF' * 12)
        
        # Write ANIMINFO and ANIMKEYS sections
        section = Section()
        section.name = PsaSectionName.ANIMINFO
        section.data_size = 176
        section.data_count = 0
        fp.write(section)
        
        section = Section()
        section.name = PsaSectionName.ANIMKEYS
        section.data_size = 32
        section.data_count = 0
        fp.write(section)
        
        # Capture stdout to check for the print message
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.psa', delete_on_close=True) as temp_file:
                temp_file.write(fp.getvalue())
                temp_path = temp_file.name
            
            try:
                reader = PsaReader(temp_path)
                reader.fp.close()
                
                output = captured_output.getvalue()
                assert "Unrecognized section in PSA" in output
                assert unknown_section_name.decode() in output
                assert len(reader.psa.bones) == 1
            finally:
                os.unlink(temp_path)
        finally:
            sys.stdout = old_stdout
