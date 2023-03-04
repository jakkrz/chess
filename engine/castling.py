from move import CastlingMove
from coordinate import Coordinate
from color import Color
from game_state.game_state import GameState
from game_state.castling_permissions import CastlingSide
import notation
from typing import List


def get_castling_king_square(move: CastlingMove) -> Coordinate:
    if move.color is Color.WHITE:
        return Coordinate.from_string("e1")
    else:
        return Coordinate.from_string("e8")


def get_castling_rook_square(move: CastlingMove) -> Coordinate:
    if move.side is CastlingSide.KINGSIDE:
        rook_file = notation.get_file_by_char("h")
    else:
        rook_file = notation.get_file_by_char("a")

    if move.color is Color.WHITE:
        rook_rank = notation.get_rank_by_char("1")
    else:
        rook_rank = notation.get_rank_by_char("8")

    return Coordinate(rook_file, rook_rank)


def get_castling_target_square(move: CastlingMove) -> Coordinate:
    if move.side is CastlingSide.KINGSIDE:
        rook_file = notation.get_file_by_char("g")
    else:
        rook_file = notation.get_file_by_char("c")

    if move.color is Color.WHITE:
        rook_rank = notation.get_rank_by_char("1")
    else:
        rook_rank = notation.get_rank_by_char("8")

    return Coordinate(rook_file, rook_rank)


def _get_numbers_between(a: int, b: int) -> List[int]:
    if a < b:
        return list(range(a + 1, b))
    else:
        return list(range(a - 1, b, -1))


def get_intermediary_squares(square_a: Coordinate, square_b: Coordinate) -> List[Coordinate]:
    if square_a.rank == square_b.rank:
        intermediary_files = _get_numbers_between(square_a.file, square_b.file)

        return [Coordinate(file, square_a.rank) for file in intermediary_files]
    elif square_a.file == square_b.file:
        intermediary_ranks = _get_numbers_between(square_a.rank, square_b.rank)

        return [Coordinate(square_a.file, rank) for rank in intermediary_ranks]
    else:
        raise ValueError("Cannot get intermediary squares: square_a and square_b don't share file nor rank.")


def get_castling_intermediary_squares(move: CastlingMove) -> List[Coordinate]:
    king_square = get_castling_king_square(move)
    rook_square = get_castling_rook_square(move)

    return get_intermediary_squares(king_square, rook_square)


def get_castling_passthrough_squares(move: CastlingMove) -> List[Coordinate]:
    king_square = get_castling_king_square(move)
    target_square = get_castling_target_square(move)

    return get_intermediary_squares(king_square, target_square)


def verify_castling_move(game_state: GameState, move: CastlingMove, color_making_move: Color) -> bool:
    from engine.threats import find_king, is_in_check, square_is_threatened_by
    from engine.move_generation import get_squares_around_square


    if move.color is not color_making_move:
        return False

    castling_permissions = game_state.castling_permissions

    if not castling_permissions.can_castle_on_side(move.color, move.side):
        return False

    # Cannot castle out of check:
    if is_in_check(game_state, color_making_move):
        return False

    enemy_king_pos = find_king(game_state.board, color_making_move.opposite())
    surrounding_enemy_king = get_squares_around_square(game_state.board, enemy_king_pos)
    # Cannot castle through check:
    for passthrough_square in get_castling_passthrough_squares(move):
        if square_is_threatened_by(game_state, passthrough_square, color_making_move.opposite(), exclude_king=True):
            return False
        elif passthrough_square in surrounding_enemy_king:
            return False

    # Cannot castle into check:
    target_square = get_castling_target_square(move)

    if square_is_threatened_by(game_state, target_square, color_making_move.opposite(), exclude_king=True):
        return False

    if target_square in surrounding_enemy_king:
        return False

    intermediary_squares = get_castling_intermediary_squares(move)

    for square in intermediary_squares:
        if not game_state.board.square_is_empty(square):
            return False

    return True
