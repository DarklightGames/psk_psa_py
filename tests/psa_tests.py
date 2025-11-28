from io import BytesIO
from pathlib import Path
from psk_psa_py.psa.config import read_psa_config
from psk_psa_py.psa.reader import PsaReader
from psk_psa_py.psa.writer import write_psa


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
    for i, (b1, b2) in enumerate(zip(input.bones, output.bones)):
        assert b1.children_count == b2.children_count
        assert b1.flags == b2.flags
        assert b1.length == b2.length
        assert b1.name == b2.name
        assert b1.parent_index == b2.parent_index
    
    # Sequences
    assert len(input.sequences) == len(output.sequences)
    for i, ((k1, s1), (k2, s2)) in enumerate(zip(input.sequences.items(), output.sequences.items())):
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

        for j, (k1, k2) in enumerate(zip(input_keys, output_keys)):
            assert k1.location == k2.location
            assert k1.rotation == k2.rotation
            assert k1.time == k2.time

        assert len(input_keys) == len(output_keys)
    

def test_psa_import_export_round_trip():
    """
    Ensures that all the data survives a round-trip from being read and written out again.
    """
    from glob import glob

    test_data_directory = './tests/data/psa'
    for filename in glob('*.psa', root_dir=test_data_directory):
        path = Path(test_data_directory) / filename
        path = path.resolve()
        _assert_psa_round_trip_data_is_unchanged(path)


def test_psa_config_read():
    psa_reader = PsaReader('./tests/data/psa/Carlos_StrafeLF90_2.psa')
    psa_sequence_names = list(psa_reader.sequences.keys())

    config_path = './tests/data/psa/Carlos_StrafeLF90_2.config'
    config = read_psa_config(psa_sequence_names, config_path)

    print(config.sequence_bone_flags)
