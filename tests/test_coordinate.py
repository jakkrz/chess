import pytest
from coordinate import Coordinate

@pytest.mark.parametrize("corresponding_string,corresponding_coord", [
    ("a4", Coordinate(0, 3)),
    ("b1", Coordinate(1, 0)),
    ("h8", Coordinate(7, 7)),
    ("f2", Coordinate(5, 1)),
])
class TestCoordinateStringConversion:
    def test_from_string(self, corresponding_string: str, corresponding_coord: Coordinate):
        assert Coordinate.from_string(corresponding_string) == corresponding_coord

    def test_str(self, corresponding_string: str, corresponding_coord: Coordinate):
        assert str(corresponding_coord) == corresponding_string

@pytest.mark.parametrize("char,file", [
    ("a", 0),
    ("b", 1),
    ("c", 2),
    ("d", 3),
    ("e", 4),
    ("f", 5),
    ("g", 6),
    ("h", 7),
])
def test_get_file_by_char(char: str, file: int):
    assert Coordinate.get_file_by_char(char) == file

@pytest.mark.parametrize("char,rank", [
    ("1", 0),
    ("2", 1),
    ("3", 2),
    ("4", 3),
    ("5", 4),
    ("6", 5),
    ("7", 6),
    ("8", 7),
])
def test_get_rank_by_char(char: str, rank: int):
    assert Coordinate.get_rank_by_char(char) == rank

@pytest.mark.parametrize("coord_a,coord_b,coord_sum", [
    (Coordinate( 0,  0), Coordinate( 0,  0), Coordinate(0,  0)),
    (Coordinate( 5,  5), Coordinate( 0,  0), Coordinate(5,  5)),
    (Coordinate( 5, -5), Coordinate( 0,  0), Coordinate(5, -5)),
    (Coordinate(-3,  2), Coordinate( 5, -3), Coordinate(2, -1)),
])
class TestCoordinateArithmetic:
    def test_coordinate_addition(self, coord_a: Coordinate, coord_b: Coordinate, coord_sum: Coordinate):
        assert coord_a + coord_b == coord_sum

    def test_coordinate_subtraction(self, coord_a: Coordinate, coord_b: Coordinate, coord_sum: Coordinate):
        assert coord_sum - coord_a == coord_b
        assert coord_sum - coord_b == coord_a

