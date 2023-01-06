from dataclasses import dataclass


@dataclass
class Move:
    """
    Move stores a move of a piece on the chess self.board. For castling, simply move the king onto
    his position after castling.
    """

    source: tuple[int, int]
    destination: tuple[int, int]

    def encode(self) -> bytes:
        first_byte = self.source[0].to_bytes(1, "big", signed=False)
        second_byte = self.source[1].to_bytes(1, "big", signed=False)
        third_byte = self.destination[0].to_bytes(1, "big", signed=False)
        fourth_byte = self.destination[1].to_bytes(1, "big", signed=False)

        return first_byte + second_byte + third_byte + fourth_byte
