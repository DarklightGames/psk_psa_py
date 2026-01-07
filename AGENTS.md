# AI Coding Instructions for psk_psa_py

## Project Overview
`psk_psa_py` is a Python library for reading and writing PSK (skeletal mesh) and PSA (animation sequence) file formats used in game engines like Unreal Engine. The project uses `ctypes.Structure` to define binary file formats with strict byte-level serialization.

## Architecture

### Core Components
- **`src/psk_psa_py/psk/`**: PSK (skeletal mesh) reader/writer for vertices, faces, bones, weights, and morph data
- **`src/psk_psa_py/psa/`**: PSA (animation sequences) reader/writer for keyframe data with lazy-loading pattern
- **`src/psk_psa_py/shared/`**: Shared data structures (`Vector3`, `Quaternion`, `Color`) and `Section` format definition

### Data Flow Pattern
1. **Reader**: Parses binary file sections sequentially, instantiates `ctypes.Structure` subclasses from raw buffers
2. **Writer**: Validates constraints (see [writer.py](src/psk_psa_py/psk/writer.py#L14-L21)), serializes structures to binary, writes sections in order
3. **PSA Special Case**: `PsaReader` holds file handle and reads keyframe data on-demand via [read_sequence_keys()](src/psk_psa_py/psa/reader.py#L59) to avoid memory overhead

### ctypes.Structure Usage Pattern
All data classes inherit from [StructureEq](src/psk_psa_py/shared/data.py#L3) (adds `__eq__`/`__ne__` to ctypes.Structure). Define `_fields_` list with ctypes types. Example:
```python
class Bone(StructureEq):
    _fields_ = [
        ('name', c_char * 64),
        ('flags', c_int32),
        ('rotation', Quaternion),  # Nested structure supported
        ('location', Vector3),
    ]
```

## Key Patterns & Conventions

### Binary Section Format
All PSK/PSA files use 20-byte [Section](src/psk_psa_py/shared/data.py#L115) headers. Reader/writer use string matching on section names (e.g., `b'PNTS0000'`, `b'REFSKELT'`) to route data. Unknown sections are skipped with warnings during read.

### Wedge Format Compatibility
PSK files may have 16-bit or 32-bit point indices in wedge data due to tool differences. [Reader logic](src/psk_psa_py/psk/reader.py#L97-L105) detects if points fit in 16-bit and truncates high bits if needed—preserves backward compatibility with older exporters.

### Material Reference Loading
Optional `.props.txt` sidecar file (from UEViewer/CUE4Parse exports) contains fully-qualified material references. [Reader](src/psk_psa_py/psk/reader.py#L13-L19) uses regex to parse `Material = ...` entries into `psk.material_references`.

### PSA Sequence Data Layout
Sequences store keyframe data contiguously. [Read logic](src/psk_psa_py/psa/reader.py#L59-L80) calculates offset as `keys_data_offset + (frame_start_index * bone_count * data_size)`. Data matrix shape is [frames, bones, 7] where 7 = [qw, qx, qy, qz, x, y, z].

### CUE4Parse Bug Workaround
Some PSA files (pre-fix) have incorrect `frame_start_index` equaling `frame_count`. [Detector](src/psk_psa_py/psa/reader.py#L6-L18) auto-fixes by recalculating indices assuming sequences have no shared frames.

## Testing & Validation

### Round-Trip Testing
Tests verify data survives read→write→read cycle. Compare structures element-by-element (ctypes arrays require explicit tuple conversion). Examples:
- [PSK round-trip](tests/psk_tests.py#L11-L73): Points, wedges, faces, materials, bones, weights, extra UVs, colors, normals, morph data
- [PSA round-trip](tests/psa_tests.py#L7-L45): Bones, sequences, keys, data matrices

### Running Tests
```bash
pytest tests/*.py -v
```

### Type Checking
```bash
mypy src/psk_psa_py
```

## Modification Guidelines

### Type Stub Files (.pyi)
**CRITICAL**: Always update corresponding `.pyi` stub files when modifying type signatures, class definitions, or function signatures in `.py` files. Stub files provide type hints for type checkers (mypy) and IDEs.
- Located alongside `.py` files: `data.py` → `data.pyi`, etc.
- Must match runtime signatures exactly
- Include all public classes, methods, and their type annotations
- Run `mypy src/psk_psa_py --check-untyped-defs` to verify correctness

### Adding New PSK Section Support
1. Define Structure subclass in [psk/data.py](src/psk_psa_py/psk/data.py)
2. Add section name case in reader's match statement ([reader.py](src/psk_psa_py/psk/reader.py#L50-L77))
3. Add parallel write code in [writer.py](src/psk_psa_py/psk/writer.py) inside `write_psk()`
4. Add list attribute to `Psk` class to store data
5. Add round-trip assertions to test file

### Handling Struct Alignment
Use `_pack_ = 1` when ctypes default alignment would cause issues. Check with `ctypes.sizeof()` to verify serialized size matches binary format expectations.

### Extended Format Support
PSK extended format includes extra UVs, normals, colors, and morph data (written only if `is_extended_format=True`). Standard format omits these.

## Dependencies
- **numpy**: Data matrix operations in PSA reader ([read_sequence_data_matrix()](src/psk_psa_py/psa/reader.py#L43-L55))
- **pytest**: Test framework
- **hatchling**: Build backend (pyproject.toml)

## Configuration Files
- [pyproject.toml](pyproject.toml): Build config, dependencies, package metadata
- [requirements.txt](requirements.txt): Development dependencies (numpy, pytest, pytest-cov, mypy)

## String Encoding
* All string fields in PSK/PSA structures use byte strings (`bytes` type).
* The tools that consume PSK/PSA files expect null-terminated Windows-1252 encoded strings.
* When creating or modifying string fields, ensure proper encoding and null-termination.
