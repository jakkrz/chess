from color import Color
from engine.castling import verify_castling_move
from game_state.castling_permissions import CastlingSide
from game_state.game_state import GameState
from game_state.board import Board
from coordinate import Coordinate
from engine.threats import find_king
from move import (
    Move,
    BasicMove,
    CastlingMove,
    EnPassantMove,
    PawnDoubleMove,
    PromotionMove
)

from piece import PieceType
from typing import Set, List

def get_squares_around_square(board: Board, square: Coordinate) -> Set[Coordinate]:
    offsets = [
        Coordinate(-1, -1),
        Coordinate( 0, -1),
        Coordinate( 1, -1),
        Coordinate(-1,  0),
        Coordinate( 1,  0),
        Coordinate(-1,  1),
        Coordinate( 0,  1),
        Coordinate( 1,  1),
    ]

    squares = set()

    for offset in offsets:
        new_pos = square + offset

        if board.contains_square(new_pos):
            squares.add(new_pos)

    return squares
            
def _generate_basic_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[BasicMove]:
    board = game_state.board
    moves = set()

    piece = board.at(piece_square)

    if piece is None:
        raise ValueError("piece_square is empty")

    king_color = piece.color
    surrounding_king = get_squares_around_square(board, piece_square)

    opposite_king_pos = find_king(board, king_color.opposite())
    surrounding_opposite_king = get_squares_around_square(board, opposite_king_pos)

    remaining_coordinates = surrounding_king - surrounding_opposite_king

    for coord in remaining_coordinates:
        piece_at_coord = board.at(coord)

        if piece_at_coord is None or piece_at_coord.color != king_color:
            moves.add(BasicMove(piece_square, coord))

    return moves


def _generate_castling_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[CastlingMove]:
    king = game_state.board.at(piece_square)

    if king is None:
        raise ValueError("piece_square is empty")

    kingside_castling_move = CastlingMove(CastlingSide.KINGSIDE, king.color)
    queenside_castling_move = CastlingMove(CastlingSide.QUEENSIDE, king.color)
    moves = set()

    if verify_castling_move(game_state, kingside_castling_move, king.color):
        moves.add(kingside_castling_move)
    if verify_castling_move(game_state, queenside_castling_move, king.color):
        moves.add(queenside_castling_move)

    return moves

def generate_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    moves = set()
    moves.update(_generate_basic_moves_for_king(game_state, piece_square))
    moves.update(_generate_castling_moves_for_king(game_state, piece_square))
    return moves


def generate_moves_for_queen(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    moves = set()

    moves.update(generate_moves_for_rook(game_state, piece_square))
    moves.update(generate_moves_for_bishop(game_state, piece_square))

    return moves

def _generate_moves_in_direction(game_state: GameState, piece_square: Coordinate, direction: Coordinate) -> Set[Move]:
    piece = game_state.board.at(piece_square)

    if piece is None:
        raise ValueError("piece at piece_square is none")

    moves = set()
    next_coordinate = piece_square + direction

    while True:
        if not game_state.board.contains_square(next_coordinate):
            break

        attacking_piece = game_state.board.at(next_coordinate)

        if attacking_piece is None:
            moves.add(BasicMove(piece_square, next_coordinate))
        elif attacking_piece.color != piece.color:
            moves.add(BasicMove(piece_square, next_coordinate))
            break
        else:
            break
        
        next_coordinate += direction

    return moves
        


def generate_moves_for_rook(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    moves = set()
    rook_attack_directions = [
        Coordinate( 1,  0),
        Coordinate(-1,  0),
        Coordinate( 0,  1),
        Coordinate( 0, -1),
    ]

    for direction in rook_attack_directions:
        moves.update(_generate_moves_in_direction(game_state, piece_square, direction))

    return moves

def generate_moves_for_knight(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    knight_move_offsets = [
        Coordinate( 2,  1),
        Coordinate( 2, -1),
        Coordinate(-2,  1),
        Coordinate(-2, -1),
        Coordinate( 1,  2),
        Coordinate( 1, -2),
        Coordinate(-1,  2),
        Coordinate(-1, -2),
    ]

    moving_knight = game_state.board.at(piece_square)

    if moving_knight is None:
        raise ValueError("piece_square does not contain knight")

    moves = set()

    for offset in knight_move_offsets:
        position = piece_square + offset

        if not game_state.board.contains_square(position):
            continue

        piece_at_pos = game_state.board.at(position)

        if piece_at_pos is None:
            moves.add(BasicMove(piece_square, position))
            continue

        if piece_at_pos.color == moving_knight.color:
            continue

        moves.add(BasicMove(piece_square, position))

    return moves



def generate_moves_for_bishop(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    moves = set()
    bishop_attack_directions = [
        Coordinate( 1,  1),
        Coordinate( 1, -1),
        Coordinate(-1,  1),
        Coordinate(-1, -1),
    ]

    for direction in bishop_attack_directions:
        moves.update(_generate_moves_in_direction(game_state, piece_square, direction))

    return moves

def _get_forward_direction_for_color(color: Color) -> int:
    if color is Color.WHITE:
        return 1
    else:
        return -1

def _square_contains_color(game_state: GameState, piece_square: Coordinate, color: Color) -> bool:
    if not game_state.board.contains_square(piece_square):
        return False

    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        return False

    return piece_at_square.color == color

def _get_promotable_piece_types() -> List[PieceType]:
    return [
        PieceType.ROOK,
        PieceType.BISHOP,
        PieceType.KNIGHT,
        PieceType.QUEEN
    ]    

def generate_moves_for_pawn(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    board = game_state.board
    en_passant_target = game_state.en_passant_target_square
    piece = board.at(piece_square)

    if piece is None:
        raise ValueError("piece_square is empty")

    moves = set()
    forward = _get_forward_direction_for_color(piece.color)
    left_diagonal  = piece_square + Coordinate(-1, forward)
    right_diagonal = piece_square + Coordinate( 1, forward)
    forward_square = piece_square + Coordinate( 0, forward)
    double_forward_square = piece_square + Coordinate(0, forward * 2)

    if _square_contains_color(game_state, left_diagonal, piece.color.opposite()):
        moves.add(BasicMove(piece_square, left_diagonal))

    if _square_contains_color(game_state, right_diagonal, piece.color.opposite()):
        moves.add(BasicMove(piece_square, right_diagonal))

    second_rank = board.get_nth_rank_for_color(2, piece.color)
    third_rank = board.get_nth_rank_for_color(3, piece.color)
    seventh_rank = board.get_nth_rank_for_color(7, piece.color)

    if board.contains_square(forward_square) and board.square_is_empty(forward_square):
        moves.add(BasicMove(piece_square, forward_square))

        if piece_square.rank == second_rank:
            if board.contains_square(double_forward_square) and board.square_is_empty(double_forward_square):
                moves.add(PawnDoubleMove(piece_square, double_forward_square))
        elif piece_square.rank == seventh_rank:
            for piece_type in _get_promotable_piece_types():
                moves.add(PromotionMove(piece_square, forward_square, piece_type))
        elif piece_square.rank == third_rank:
            if left_diagonal == en_passant_target:
                moves.add(EnPassantMove(piece_square, left_diagonal))
            elif right_diagonal == en_passant_target:
                moves.add(EnPassantMove(piece_square, right_diagonal))

    return moves
    

def generate_moves_for_piece(game_state: GameState, piece_square: Coordinate, must_evade_check: bool = True) -> Set[Move]:
    from engine.engine import move_evades_check

    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        return set()

    piece_type = piece_at_square.piece_type
    color = piece_at_square.color

    if piece_type == PieceType.KING:
        result = generate_moves_for_king(game_state, piece_square)
    elif piece_type == PieceType.QUEEN:
        result = generate_moves_for_queen(game_state, piece_square)
    elif piece_type == PieceType.ROOK:
        result = generate_moves_for_rook(game_state, piece_square)
    elif piece_type == PieceType.KNIGHT:
        result = generate_moves_for_knight(game_state, piece_square)
    elif piece_type == PieceType.BISHOP:
        result = generate_moves_for_bishop(game_state, piece_square)
    else:
        result = generate_moves_for_pawn(game_state, piece_square)

    if must_evade_check:
        result = set(filter(lambda move: move_evades_check(game_state, move, color), result))

    return result
