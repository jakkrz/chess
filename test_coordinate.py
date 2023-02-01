import unittest
from coordinate import Coordinate


class CoordinateTest(unittest.TestCase):

    def string_conversion_pair(self, input_string):
        with self.subTest(input=input_string):
            self.assertEqual(str(Coordinate.from_string(input_string)),
                             input_string)

    def string_produces_coord(self, coord_string, expected_coord):
        with self.subTest(input=coord_string, expected=expected_coord):
            gotten_coord = Coordinate.from_string(coord_string)

            self.assertEqual(gotten_coord, expected_coord)

    def _test_coord_string(self, coord_string, expected_file, expected_rank):
        coord = Coordinate.from_string(coord_string)
        file = coord.file
        rank = coord.rank

        self.assertEqual(file, expected_file)
        self.assertEqual(rank, expected_rank)

    def test_from_string(self):
        self.string_conversion_pair("e4")
        self.string_produces_coord("e4", Coordinate(4, 3))
        self.string_produces_coord("a1", Coordinate(0, 0))
        self.string_produces_coord("h8", Coordinate(7, 7))
