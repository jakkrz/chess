from dataclasses import dataclass
from enum import Enum, auto


class PieceType(Enum):
    KING = auto()
    QUEEN = auto()
    BISHOP = auto()
    HORSE = auto()
    CASTLE = auto()
    PAWN = auto()


@dataclass
class Piece:
    is_white: bool
    piece_type: PieceType
