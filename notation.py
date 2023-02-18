from piece import Piece, PieceType
from color import Color

def get_piece_by_character(character: str):
    color = Color.WHITE if character.isupper() else Color.BLACK

    lower_character = character.lower()

    if lower_character == "k":
        piece_type = PieceType.KING
    elif lower_character == "q":
        piece_type = PieceType.QUEEN
    elif lower_character == "n":
        piece_type = PieceType.KNIGHT
    elif lower_character == "r":
        piece_type = PieceType.ROOK
    elif lower_character == "p":
        piece_type = PieceType.PAWN
    elif lower_character == "b":
        piece_type = PieceType.BISHOP
    else:
        raise ValueError(character)

    return Piece(color, piece_type)
