from color import Color
from piece import PieceType
from enum import Enum, auto
import notation

class CastlingSide(Enum):
    KINGSIDE = auto()
    QUEENSIDE = auto()

class CastlingPermissions:
    def __init__(self):
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True

    def __str__(self) -> str:
        result = ""

        if self.white_kingside:
            result += "K"
        if self.white_queenside:
            result += "Q"
        if self.black_kingside:
            result += "k"
        if self.black_queenside:
            result += "q"

        if result == "":
            return "-"

        return result
            
    def __repr__(self) -> str:
        return f"<CastlingPermissions:{self}>"
        
    def can_castle_on_side(self, color: Color, side: CastlingSide):
        if color is Color.WHITE:
            if side is CastlingSide.KINGSIDE:
                return self.white_kingside
            elif side is CastlingSide.QUEENSIDE:
                return self.white_queenside
        elif color is Color.BLACK:
            if side is CastlingSide.KINGSIDE:
                return self.black_kingside
            elif side is CastlingSide.QUEENSIDE:
                return self.black_queenside

    def set_can_castle_on_side(self, color: Color, side: CastlingSide, can_castle):
        if color is Color.WHITE:
            if side is CastlingSide.KINGSIDE:
                self.white_kingside = can_castle
            elif side is CastlingSide.QUEENSIDE:
                self.white_queenside = can_castle
        elif color is Color.BLACK:
            if side is CastlingSide.KINGSIDE:
                self.black_kingside = can_castle
            elif side is CastlingSide.QUEENSIDE:
                self.black_queenside = can_castle

    def disable_all_castling_for_color(self, color: Color):
        self.set_can_castle_on_side(color, CastlingSide.KINGSIDE, False)
        self.set_can_castle_on_side(color, CastlingSide.QUEENSIDE, False)

    def disable_all_castling(self):
        self.disable_all_castling_for_color(Color.WHITE)
        self.disable_all_castling_for_color(Color.BLACK)

    @staticmethod
    def from_string(string: str):
        result = CastlingPermissions()

        if string == "-":
            return result

        for character in string:
            piece = notation.get_piece_by_character(character)

            if piece.piece_type is PieceType.KING:
                result.set_can_castle_on_side(piece.color, CastlingSide.KINGSIDE, True)
            elif piece.piece_type is PieceType.QUEEN:
                result.set_can_castle_on_side(piece.color, CastlingSide.QUEENSIDE, True)
            else:
                raise ValueError(character)

        return result
