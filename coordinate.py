from dataclasses import dataclass
import notation


@dataclass
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

        file = notation.get_file_by_char(string[0])
        rank = notation.get_rank_by_char(string[1])

        return Coordinate(file, rank)

    def __add__(self, other: "Coordinate"):
        return Coordinate(self.file + other.file, self.rank + other.rank)

    def __hash__(self) -> int:
        return hash(self.file) ^ hash(self.rank)
