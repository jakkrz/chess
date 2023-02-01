class Coordinate:

    def __init__(self, file, rank):
        self.file = file
        self.rank = rank

    @staticmethod
    def from_string(string):
        if len(string) != 2:
            raise ValueError(string)

        file = Coordinate._get_file_from_char(string[0])
        rank = Coordinate._get_rank_from_char(string[1])

        return Coordinate(file, rank)

    @staticmethod
    def _get_file_from_char(char):
        num_in_alphabet = Coordinate._get_char_number_in_alphabet(char.lower())

        if num_in_alphabet < 0 or num_in_alphabet > 7:
            raise ValueError(char)

        return num_in_alphabet

    @staticmethod
    def _get_rank_from_char(char):
        try:
            return int(char) - 1
        except ValueError:
            raise ValueError(char)

    @staticmethod
    def _get_char_number_in_alphabet(char):
        return ord(char) - 97

    def _get_nth_char_in_alphabet(self, n):
        return chr(97 + n)

    def __repr__(self):
        file_char = self._get_nth_char_in_alphabet(self.file)
        rank_char = str(self.rank + 1)

        return file_char + rank_char

    def __eq__(self, other):
        return self.file == other.file and self.rank == other.rank
