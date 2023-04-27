from typing import Type, Dict
from color import Color
from move import (
    Move,
    CastlingMove,
    PawnDoubleMove,
    EnPassantMove,
    PromotionMove,
    BasicMove
)
from game_state.game_state import GameState
from parsing.fen_parser import FenParser
from coordinate import Coordinate
from notation import (
    get_piece_by_character,
    get_character_by_piece,
    get_castling_move_by_character,
    get_character_by_castling_move
)
from piece import Piece


MOVE_TYPE_SPECIFIERS: Dict[Type[Move], bytes] = {
    BasicMove: b"b",
    PawnDoubleMove: b"d",
    EnPassantMove: b"e",
    PromotionMove: b"p",
    CastlingMove: b"c",
}


def serialize_coordinate(coordinate: Coordinate) -> bytes:
    return repr(coordinate).encode()


def deserialize_coordinate(coordinate_bytes: bytes) -> Coordinate:
    return Coordinate.from_string(coordinate_bytes.decode(encoding="ascii"))


def serialize_piece(piece: Piece) -> bytes:
    return get_character_by_piece(piece).encode()


def deserialize_piece(piece_bytes: bytes) -> Piece:
    return get_piece_by_character(piece_bytes.decode(encoding="ascii"))


def serialize_move(move: Move) -> bytes:
    type_specifier = MOVE_TYPE_SPECIFIERS[type(move)]

    if isinstance(move, BasicMove):
        return type_specifier + serialize_basic_move(move)
    elif isinstance(move, PawnDoubleMove):
        return type_specifier + serialize_pawn_double_move(move)
    elif isinstance(move, PromotionMove):
        return type_specifier + serialize_promotion_move(move)
    elif isinstance(move, CastlingMove):
        return type_specifier + serialize_castling_move(move)
    elif isinstance(move, EnPassantMove):
        return type_specifier + serialize_en_passant_move(move)
    else:
        raise ValueError("invalid move type")


def serialize_basic_move(move: BasicMove) -> bytes:
    return serialize_coordinate(move.source_square) + serialize_coordinate(move.target_square)


def serialize_pawn_double_move(move: PawnDoubleMove) -> bytes:
    return serialize_coordinate(move.source_square) + serialize_coordinate(move.target_square)


def serialize_castling_move(move: CastlingMove) -> bytes:
    return get_character_by_castling_move(move).encode()


def serialize_en_passant_move(move: EnPassantMove) -> bytes:
    return serialize_coordinate(move.source_square) + serialize_coordinate(move.target_square)


def serialize_promotion_move(move: PromotionMove) -> bytes:
    return serialize_coordinate(move.source_square) + serialize_coordinate(move.target_square) + serialize_piece(Piece(Color.WHITE, move.promote_to))


def deserialize_move(move_bytes: bytes) -> Move:
    initial_byte = move_bytes[0:1]
    remaining_bytes = move_bytes[1:]

    move_type = get_dict_index_for_value(MOVE_TYPE_SPECIFIERS, initial_byte)

    if move_type is None:
        raise ValueError("Invalid move type specifier")

    if move_type is BasicMove:
        return deserialize_basic_move(remaining_bytes)
    elif move_type is PromotionMove:
        return deserialize_promotion_move(remaining_bytes)
    elif move_type is EnPassantMove:
        return deserialize_en_passant_move(remaining_bytes)
    elif move_type is PawnDoubleMove:
        return deserialize_pawn_double_move(remaining_bytes)
    elif move_type is CastlingMove:
        return deserialize_castling_move(remaining_bytes)
    else:
        raise ValueError("invalid move type")
        

def get_dict_index_for_value(_dict, value):
    for key, value_in_dict in _dict.items():
        if value_in_dict == value:
            return key

    return None

    
def deserialize_basic_move(move_bytes: bytes) -> BasicMove:
    return BasicMove(deserialize_coordinate(move_bytes[0:2]), deserialize_coordinate(move_bytes[2:4]))


def deserialize_pawn_double_move(move_bytes: bytes) -> PawnDoubleMove:
    return PawnDoubleMove(deserialize_coordinate(move_bytes[0:2]), deserialize_coordinate(move_bytes[2:4]))


def deserialize_castling_move(move_bytes: bytes) -> CastlingMove:
    return get_castling_move_by_character(move_bytes.decode(encoding="ascii"))


def deserialize_en_passant_move(move_bytes: bytes) -> EnPassantMove:
    return EnPassantMove(deserialize_coordinate(move_bytes[0:2]), deserialize_coordinate(move_bytes[2:4]))


def deserialize_promotion_move(move_bytes: bytes) -> PromotionMove:
    # slice of [4:5] to avoid returning int
    return PromotionMove(deserialize_coordinate(move_bytes[0:2]), deserialize_coordinate(move_bytes[2:4]), deserialize_piece(move_bytes[4:5]).piece_type)


def serialize_game_state(game_state: GameState) -> bytes:
    fen_parser = FenParser()

    return fen_parser.serialize(game_state).encode()


def deserialize_game_state(game_state_bytes: bytes) -> GameState:
    fen_parser = FenParser()

    return fen_parser.parse(game_state_bytes.decode(encoding="ascii"))


def serialize_color(color: Color) -> bytes:
    if color is Color.WHITE:
        return b"w"
    else:
        return b"b"


def deserialize_color(color_bytes: bytes) -> Color:
    if color_bytes == b"w":
        return Color.WHITE
    elif color_bytes == b"b":
        return Color.BLACK
    else:
        raise ValueError("Cannot convert bytes to color")
