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
from parser.fen_parser import FenParser


def serialize_move(move: Move) -> bytes:
    # TODO
    pass


def deserialize_move(move_bytes: bytes) -> Move:
    # TODO
    pass


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
