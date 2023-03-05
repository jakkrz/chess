from move import CastlingMove
from coordinate import Coordinate
from color import Color
from game_state.game_state import GameState
from game_state.castling_permissions import CastlingSide
import notation
from typing import List




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
