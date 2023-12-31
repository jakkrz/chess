from piece import Piece, PieceType
from color import Color
from move import CastlingMove
from castling_side import CastlingSide


def get_character_by_piece(piece: Piece) -> str:
    result = ""

    if piece.piece_type is PieceType.KING:
        result = "k"
    elif piece.piece_type is PieceType.QUEEN:
        result = "q"
    elif piece.piece_type is PieceType.KNIGHT:
        result = "n"
    elif piece.piece_type is PieceType.ROOK:
        result = "r"
    elif piece.piece_type is PieceType.PAWN:
        result = "p"
    elif piece.piece_type is PieceType.BISHOP:
        result = "b"

    if piece.color is Color.WHITE:
        return result.upper()

    return result


def get_piece_by_character(character: str) -> Piece:
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


def _get_char_number_in_alphabet(char: str):
    return ord(char) - 97


def get_file_by_char(char: str) -> int:
    num_in_alphabet = _get_char_number_in_alphabet(char.lower())

    if num_in_alphabet < 0 or num_in_alphabet > 7:
        raise ValueError(char)

    return num_in_alphabet


def get_rank_by_char(char: str) -> int:
    try:
        return int(char) - 1
    except ValueError:
        raise ValueError(char)


def get_color_by_char(char: str) -> Color:
    if char == "w":
        return Color.WHITE
    elif char == "b":
        return Color.BLACK
    else:
        raise ValueError(char)


def get_char_by_color(color: Color) -> str:
    if color is Color.WHITE:
        return "w"
    elif color is Color.BLACK:
        return "b"


def get_character_by_castling_move(move: CastlingMove):
    if move.side is CastlingSide.KINGSIDE:
        side_char = "k"
    else:
        side_char = "q"

    if move.color is Color.WHITE:
        return side_char.upper()
    else:
        return side_char.lower()


def get_castling_move_by_character(char: str):
    if char.isupper():
        color = Color.WHITE
    else:
        color = Color.BLACK

    side_char = char.lower()

    if side_char == "k":
        side = CastlingSide.KINGSIDE
    else:
        side = CastlingSide.QUEENSIDE

    return CastlingMove(side, color)

