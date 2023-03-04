from coordinate import Coordinate
from game_state.board import Board
from game_state.game_state import GameState
from piece import Piece, PieceType
from typing import Optional
from move import (
    BasicMove,
    EnPassantMove
)
from color import Color

def find_piece(board: Board, target_piece: Piece) -> Optional[Coordinate]:
    for rank_index, rank in enumerate(board.matrix):
        for file_index, piece in enumerate(rank):
            if piece == target_piece:
                return Coordinate(file_index, rank_index)

    return None

def find_king(board: Board, color: Color) -> Coordinate:
    king_pos = find_piece(board, Piece(color, PieceType.KING))

    if king_pos is None:
        raise ValueError

    return king_pos

def square_is_threatened_by(game_state: GameState, square: Coordinate, color: Color, exclude_king=False) -> bool:
    from engine.move_generation import generate_moves_for_piece

    for rank_index, rank in enumerate(game_state.board.matrix):
        for file_index, piece in enumerate(rank):
            if piece is None or piece.color is color:
                continue

            if exclude_king and piece.piece_type is PieceType.KING:
                continue

            piece_coordinate = Coordinate(file_index, rank_index)
            possible_moves = generate_moves_for_piece(game_state, piece_coordinate, must_evade_check=False)

            if not isinstance(possible_moves, BasicMove) and not isinstance(possible_moves, EnPassantMove):
                continue

            if square == possible_moves.target_square:
                return True

    return False

def is_in_check(game_state: GameState, color: Color) -> bool:
    king_pos = find_king(game_state.board, color)
    return square_is_threatened_by(game_state, king_pos, color.opposite(), exclude_king=True)
