from game_state.castling_permissions import CastlingSide
from coordinate import Coordinate
from dataclasses import dataclass
from color import Color
from piece import PieceType

class Move:
    pass


@dataclass
class BasicMove(Move):
    source_square: Coordinate
    target_square: Coordinate

    def __hash__(self) -> int:
        return hash(self.source_square) ^ hash(self.target_square)

@dataclass
class CastlingMove(Move):
    side: CastlingSide
    color: Color

    def __hash__(self) -> int:
        return hash(self.side) ^ hash(self.color)

    
@dataclass
class EnPassantMove(Move):
    source_square: Coordinate
    target_square: Coordinate

    def __hash__(self) -> int:
        return hash(self.source_square) ^ hash(self.target_square)

@dataclass
class PawnDoubleMove(Move):
    source_square: Coordinate
    target_square: Coordinate

    def __hash__(self) -> int:
        return hash(self.source_square) ^ hash(self.target_square)

@dataclass
class PromotionMove(Move):
    source_square: Coordinate
    target_square: Coordinate
    promote_to: PieceType

    def __hash__(self) -> int:
        return hash(self.source_square) ^ hash(self.target_square) ^ hash(self.promote_to)
