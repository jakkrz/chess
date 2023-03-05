from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Coordinate:
    file: int
    rank: int

    def __repr__(self):
        file_char = self._get_nth_char_in_alphabet(self.file)
        rank_char = str(self.rank + 1)

        return file_char + rank_char

    def _get_nth_char_in_alphabet(self, n):
        return chr(97 + n)

    @staticmethod
    def from_string(string):
        if len(string) != 2:
            raise ValueError(string)

        file = Coordinate.get_file_by_char(string[0])
        rank = Coordinate.get_rank_by_char(string[1])

        return Coordinate(file, rank)

    def __add__(self, other: "Coordinate"):
        return Coordinate(self.file + other.file, self.rank + other.rank)

    def __sub__(self, other: "Coordinate"):
        return Coordinate(self.file - other.file, self.rank - other.rank)

    @staticmethod
    def _get_char_number_in_alphabet(char: str):
        return ord(char) - 97

    @staticmethod
    def get_file_by_char(char: str) -> int:
        num_in_alphabet = Coordinate._get_char_number_in_alphabet(char.lower())

        if num_in_alphabet < 0 or num_in_alphabet > 7:
            raise ValueError(char)

        return num_in_alphabet

    @staticmethod
    def get_rank_by_char(char: str) -> int:
        try:
            return int(char) - 1
        except ValueError:
            raise ValueError(char)
