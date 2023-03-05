from enum import Enum, auto
from dataclasses import dataclass
from color import Color

class PieceType(Enum):
    KING = auto()
    QUEEN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    PAWN = auto()

@dataclass(unsafe_hash=True)
class Piece:
    color: Color
    piece_type: PieceType

    def __repr__(self) -> str:
        return f"<{self.color.name} {self.piece_type.name}>"
