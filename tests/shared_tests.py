import pytest
from psk_psa_py.shared.data import Color, Vector2, Vector3, Quaternion, PsxBone, Section


class TestColor:
    def test_iter(self):
        """Test that Color.__iter__ yields all color components in order."""
        color = Color(255, 128, 64, 32)
        values = list(color)
        assert values == [255, 128, 64, 32]

    def test_iter_tuple_conversion(self):
        """Test that Color can be converted to tuple via iteration."""
        color = Color(100, 150, 200, 255)
        assert tuple(color) == (100, 150, 200, 255)

    def test_normalized(self):
        """Test that Color.normalized() returns values divided by 255."""
        color = Color(255, 128, 0, 64)
        normalized = color.normalized()
        assert normalized == (1.0, 128/255.0, 0.0, 64/255.0)

    def test_normalized_black(self):
        """Test normalized() with black color."""
        color = Color(0, 0, 0, 0)
        assert color.normalized() == (0.0, 0.0, 0.0, 0.0)

    def test_normalized_white(self):
        """Test normalized() with white color."""
        color = Color(255, 255, 255, 255)
        assert color.normalized() == (1.0, 1.0, 1.0, 1.0)

    def test_equality(self):
        """Test Color equality comparison."""
        color1 = Color(255, 128, 64, 32)
        color2 = Color(255, 128, 64, 32)
        color3 = Color(255, 128, 64, 33)
        assert color1 == color2
        assert color1 != color3

    def test_repr(self):
        """Test Color.__repr__ returns tuple representation."""
        color = Color(100, 150, 200, 255)
        assert repr(color) == "(100, 150, 200, 255)"


class TestVector2:
    def test_iter(self):
        """Test that Vector2.__iter__ yields x and y components."""
        vec = Vector2(3.5, 7.25)
        values = list(vec)
        assert len(values) == 2
        assert values[0] == 3.5
        assert values[1] == 7.25

    def test_iter_tuple_conversion(self):
        """Test that Vector2 can be converted to tuple via iteration."""
        vec = Vector2(1.0, 2.0)
        assert len(tuple(vec)) == 2

    def test_repr(self):
        """Test Vector2.__repr__ returns tuple representation."""
        vec = Vector2(1.5, 2.5)
        assert repr(vec) == "(1.5, 2.5)"

    def test_equality(self):
        """Test Vector2 equality comparison."""
        vec1 = Vector2(1.0, 2.0)
        vec2 = Vector2(1.0, 2.0)
        vec3 = Vector2(1.0, 2.1)
        assert vec1 == vec2
        assert vec1 != vec3


class TestVector3:
    def test_iter(self):
        """Test that Vector3.__iter__ yields x, y, and z components."""
        vec = Vector3(1.0, 2.0, 3.0)
        values = list(vec)
        assert len(values) == 3
        assert values[0] == 1.0
        assert values[1] == 2.0
        assert values[2] == 3.0

    def test_iter_tuple_conversion(self):
        """Test that Vector3 can be converted to tuple via iteration."""
        vec = Vector3(4.5, 5.5, 6.5)
        assert len(tuple(vec)) == 3

    def test_repr(self):
        """Test Vector3.__repr__ returns tuple representation."""
        vec = Vector3(1.0, 2.0, 3.0)
        assert repr(vec) == "(1.0, 2.0, 3.0)"

    def test_zero_factory(self):
        """Test Vector3.zero() class method returns zero vector."""
        zero = Vector3.zero()
        assert zero.x == 0.0
        assert zero.y == 0.0
        assert zero.z == 0.0

    def test_equality(self):
        """Test Vector3 equality comparison."""
        vec1 = Vector3(1.0, 2.0, 3.0)
        vec2 = Vector3(1.0, 2.0, 3.0)
        vec3 = Vector3(1.0, 2.0, 3.1)
        assert vec1 == vec2
        assert vec1 != vec3


class TestQuaternion:
    def test_iter(self):
        """Test that Quaternion.__iter__ yields w, x, y, z components in that order."""
        quat = Quaternion(1.0, 2.0, 3.0, 4.0)  # x, y, z, w
        values = list(quat)
        assert len(values) == 4
        # __iter__ yields w, x, y, z
        assert values[0] == 4.0  # w
        assert values[1] == 1.0  # x
        assert values[2] == 2.0  # y
        assert values[3] == 3.0  # z

    def test_iter_tuple_conversion(self):
        """Test that Quaternion can be converted to tuple via iteration."""
        quat = Quaternion(0.0, 0.0, 0.0, 1.0)
        assert len(tuple(quat)) == 4

    def test_repr(self):
        """Test Quaternion.__repr__ returns tuple representation."""
        quat = Quaternion(0.0, 0.0, 0.0, 1.0)
        # __repr__ yields w, x, y, z order
        assert repr(quat) == "(1.0, 0.0, 0.0, 0.0)"

    def test_identity_factory(self):
        """Test Quaternion.identity() class method returns identity quaternion."""
        identity = Quaternion.identity()
        assert identity.x == 0.0
        assert identity.y == 0.0
        assert identity.z == 0.0
        assert identity.w == 1.0

    def test_equality(self):
        """Test Quaternion equality comparison."""
        quat1 = Quaternion(0.0, 0.0, 0.0, 1.0)
        quat2 = Quaternion(0.0, 0.0, 0.0, 1.0)
        quat3 = Quaternion(0.1, 0.0, 0.0, 1.0)
        assert quat1 == quat2
        assert quat1 != quat3


class TestPsxBone:
    def test_structure_creation(self):
        """Test PsxBone can be created with all fields."""
        bone = PsxBone()
        bone.name = b"TestBone"
        bone.flags = 0
        bone.children_count = 2
        bone.parent_index = -1
        bone.rotation = Quaternion(0.0, 0.0, 0.0, 1.0)
        bone.location = Vector3(1.0, 2.0, 3.0)
        bone.length = 10.5
        bone.size = Vector3(1.0, 1.0, 1.0)

        assert bone.name == b"TestBone"
        assert bone.flags == 0
        assert bone.children_count == 2
        assert bone.parent_index == -1
        assert bone.length == 10.5

    def test_equality(self):
        """Test PsxBone equality comparison."""
        bone1 = PsxBone()
        bone1.name = b"Bone1"
        bone1.flags = 0
        bone1.children_count = 1
        bone1.parent_index = -1
        bone1.rotation = Quaternion.identity()
        bone1.location = Vector3.zero()
        bone1.length = 5.0
        bone1.size = Vector3(1.0, 1.0, 1.0)

        bone2 = PsxBone()
        bone2.name = b"Bone1"
        bone2.flags = 0
        bone2.children_count = 1
        bone2.parent_index = -1
        bone2.rotation = Quaternion.identity()
        bone2.location = Vector3.zero()
        bone2.length = 5.0
        bone2.size = Vector3(1.0, 1.0, 1.0)

        assert bone1 == bone2

        bone2.flags = 1
        assert bone1 != bone2


class TestSection:
    def test_equality(self):
        """Test Section equality comparison."""
        section1 = Section()
        section1.name = b"TEST"
        section1.data_size = 50
        section1.data_count = 5

        section2 = Section()
        section2.name = b"TEST"
        section2.data_size = 50
        section2.data_count = 5

        assert section1 == section2

        section2.data_count = 6
        assert section1 != section2


class TestStructureEq:
    def test_ne_operator(self):
        """Test that StructureEq implements __ne__ correctly."""
        vec1 = Vector3(1.0, 2.0, 3.0)
        vec2 = Vector3(1.0, 2.0, 3.0)
        vec3 = Vector3(4.0, 5.0, 6.0)

        assert not (vec1 != vec2)
        assert vec1 != vec3
