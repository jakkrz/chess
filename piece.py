from enum import Enum, auto


class PieceType(Enum):
    KING = auto()
    QUEEN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    PAWN = auto()


class Piece:

    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type

    def __repr__(self):
        return f"<{self.color.name} {self.piece_type.name}>"

    def __hash__(self):
        return hash((self.color, self.piece_type))

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False

        return self.color == other.color and self.piece_type == other.piece_type
