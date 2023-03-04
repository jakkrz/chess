from coordinate import Coordinate
from game_state.game_state import GameState
from color import Color
from copy import deepcopy
from engine.castling import verify_castling_move
from engine.move_generation import generate_moves_for_piece
from engine.threats import is_in_check
import notation


from move import (
    Move,
    BasicMove, 
    CastlingMove,
    EnPassantMove,
    PawnDoubleMove,
    PromotionMove
)


def get_files_between_files(file_a: int, file_b: int):
    if file_a < file_b:
        return list(range(file_a + 1, file_b))
    else:
        return list(range(file_a - 1, file_b, -1))

def verify_basic_move(game_state: GameState, move: BasicMove) -> bool:
    return move in generate_moves_for_piece(game_state, move.source_square, must_evade_check=True)

def verify_pawn_double_move(game_state: GameState, move: PawnDoubleMove) -> bool:
    second_rank = game_state.board.get_nth_rank_for_color(2, game_state.color_to_move)
    third_rank = game_state.board.get_nth_rank_for_color(3, game_state.color_to_move)
    fourth_rank = game_state.board.get_nth_rank_for_color(4, game_state.color_to_move)

    if move.source_square.rank != second_rank:
        return False

    if move.target_square.rank != fourth_rank:
        return False

    if move.source_square.file != move.target_square.file:
        return False

    file = move.source_square.file

    if game_state.board.at(Coordinate(file, third_rank)) is not None:
        return False

    if game_state.board.at(Coordinate(file, fourth_rank)) is not None:
        return False

    return True


def verify_promotion_move(game_state: GameState, move: PromotionMove) -> bool:
    return move in generate_moves_for_piece(game_state, move.source_square, must_evade_check=True)

def _verify_en_passant_rank(en_passant_target_rank: int, source_rank: int):
    if en_passant_target_rank == notation.get_rank_by_char("3"):
        return source_rank == notation.get_rank_by_char("4")
    elif en_passant_target_rank == notation.get_rank_by_char("6"):
        return source_rank == notation.get_rank_by_char("5")
    else:
        raise ValueError("invalid en passant target rank")

def verify_en_passant_move(game_state: GameState, move: EnPassantMove) -> bool:
    en_passant_target = game_state.en_passant_target_square

    if en_passant_target is None:
        return False

    evades_check = move in generate_moves_for_piece(game_state, move.source_square, must_evade_check=True)

    if not evades_check:
        return False

    if en_passant_target != move.target_square:
        return False

    file_distance = abs(move.source_square.file - en_passant_target.file)

    if file_distance != 1:
        return False

    if not _verify_en_passant_rank(en_passant_target.rank, move.source_square.rank):
        return False

    return True

def verify_move(game_state: GameState, move: Move, color_making_move: Color) -> bool:
    if game_state.color_to_move is not color_making_move:
        return False

    if isinstance(move, CastlingMove):
        return verify_castling_move(game_state, move, color_making_move)
    elif isinstance(move, BasicMove):
        return verify_basic_move(game_state, move)
    elif isinstance(move, PawnDoubleMove):
        return verify_pawn_double_move(game_state, move)
    elif isinstance(move, PromotionMove):
        return verify_promotion_move(game_state, move)
    elif isinstance(move, EnPassantMove):
        return verify_en_passant_move(game_state, move)
    else:
        raise ValueError("unknown move type")


def do_move(game_state: GameState, move: Move):
    pass


def move_evades_check(game_state: GameState, move: Move, color: Color):
    game_state_copy = deepcopy(game_state)
    do_move(game_state_copy, move)

    return not is_in_check(game_state_copy, color)

