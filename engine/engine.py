from typing import Set, Optional
from game_state.game_state import GameState
from game_state.board import Board
from move import (
    Move,
    BasicMove,
    EnPassantMove,
    PawnDoubleMove,
    CastlingMove,
    PromotionMove
)
from coordinate import Coordinate
from copy import deepcopy
from color import Color
from piece import Piece, PieceType
from engine.castling_squares import (
    get_castling_king_target_square,
    get_castling_rook_target_square,
    get_castling_intermediary_squares,
    get_castling_passthrough_squares,
    get_castling_king_square,
    get_castling_rook_square
)
from castling_side import CastlingSide


def verify_move(game_state: GameState, move: Move) -> bool:
    return move in generate_moves(game_state)


def is_in_checkmate(game_state: GameState) -> bool:
    return generate_moves(game_state) == set()


def generate_moves(game_state: GameState) -> Set[Move]:
    result = set()

    for rank, piece_row in enumerate(game_state.board.matrix):
        for file, piece in enumerate(piece_row):
            if piece is None:
                continue

            if piece.color is not game_state.color_to_move:
                continue

            piece_square = Coordinate(file, rank)
            result.update(generate_moves_for_piece(game_state, piece_square))

    return result


def generate_moves_for_piece(game_state: GameState, piece_square: Coordinate, must_evade_check: bool = True) -> Set[Move]:
    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        print(piece_square)
        raise ValueError("no piece at square")

    if piece_at_square.piece_type is PieceType.QUEEN:
        result = generate_moves_for_queen(game_state, piece_square)
    elif piece_at_square.piece_type is PieceType.BISHOP:
        result = generate_moves_for_bishop(game_state, piece_square)
    elif piece_at_square.piece_type is PieceType.ROOK:
        result = generate_moves_for_rook(game_state, piece_square)
    elif piece_at_square.piece_type is PieceType.KNIGHT:
        result = generate_moves_for_knight(game_state, piece_square)
    elif piece_at_square.piece_type is PieceType.KING:
        result = generate_moves_for_king(game_state, piece_square)
    else:
        result = generate_moves_for_pawn(game_state, piece_square)
    
    if must_evade_check:
        result = filter_moves_evading_check(game_state, result)

    return result


def generate_moves_for_queen(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    result = set()

    result.update(generate_moves_for_rook(game_state, piece_square))
    result.update(generate_moves_for_bishop(game_state, piece_square))

    return result


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


def generate_moves_for_knight(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    knight_move_offsets = set([
        Coordinate( 2,  1),
        Coordinate( 2, -1),
        Coordinate(-2,  1),
        Coordinate(-2, -1),
        Coordinate( 1,  2),
        Coordinate( 1, -2),
        Coordinate(-1,  2),
        Coordinate(-1, -2),
    ])

    moving_knight = game_state.board.at(piece_square)

    if moving_knight is None:
        raise ValueError("piece_square is empty")

    result = set()
    target_squares = apply_offsets_to_square(game_state, piece_square, knight_move_offsets)

    for target_square in target_squares:
        piece_at_pos = game_state.board.at(target_square)

        if piece_at_pos is None:
            result.add(BasicMove(piece_square, target_square))
            continue

        if piece_at_pos.color == moving_knight.color:
            continue

        result.add(BasicMove(piece_square, target_square))

    return result


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


def generate_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    result = set()

    result.update(generate_basic_moves_for_king(game_state, piece_square))
    result.update(generate_castling_moves_for_king(game_state, piece_square))

    return result


def generate_basic_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[BasicMove]:
    result = set()
    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        raise ValueError("piece_square is empty")

    enemy_king_color = piece_at_square.color.opposite()
    enemy_king_square = get_king_square(game_state, enemy_king_color)
    squares_surrounding_enemy_king = get_surrounding_squares(game_state, enemy_king_square)

    squares_surrounding_king = get_surrounding_squares(game_state, piece_square)

    unblocked_squares_surrounding_king = squares_surrounding_king - squares_surrounding_enemy_king

    for unblocked_square in unblocked_squares_surrounding_king:
        if game_state.board.square_is_empty(unblocked_square) or square_contains_color(game_state, unblocked_square, enemy_king_color):
            result.add(BasicMove(piece_square, unblocked_square))

    return result


def generate_castling_moves_for_king(game_state: GameState, piece_square: Coordinate) -> Set[CastlingMove]:
    result = set()
    castling_perms = game_state.castling_permissions
    piece_at_square = game_state.board.at(piece_square)
    
    if piece_at_square is None:
        raise ValueError("piece_square is empty")

    piece_color = piece_at_square.color

    castling_moves = [
        CastlingMove(CastlingSide.KINGSIDE, piece_color),
        CastlingMove(CastlingSide.QUEENSIDE, piece_color),
    ]

    for move in castling_moves:
        intermediary_squares = get_castling_intermediary_squares(move)

        if not castling_perms.can_castle_on_side(move.color, move.side):
            continue

        if not squares_are_empty(game_state, intermediary_squares):
            continue

        passthrough_squares = get_castling_passthrough_squares(move)

        for passthrough_square in passthrough_squares:
            if square_is_threatened(game_state, passthrough_square, piece_color.opposite()):
                continue

        target_square = get_castling_king_target_square(move)

        if square_is_threatened(game_state, target_square, piece_color.opposite()):
            continue

        result.add(move)

    return result


def squares_are_empty(game_state: GameState, squares: Set[Coordinate]) -> bool:
    for square in squares:
        if not game_state.board.square_is_empty(square):
            return False

    return True


def generate_moves_for_pawn(game_state: GameState, piece_square: Coordinate) -> Set[Move]:
    result_without_promotion_moves = set()
    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        raise ValueError("piece_square is empty")

    piece_color = piece_at_square.color

    second_rank = game_state.board.get_nth_rank_for_color(2, piece_color)
    eigth_rank = game_state.board.get_nth_rank_for_color(8, piece_color)

    forward = get_forward_direction_for_color(piece_color)

    if piece_square.rank == eigth_rank:
        return result_without_promotion_moves

    forward_square = Coordinate(piece_square.file, piece_square.rank + forward)
    double_forward_square = Coordinate(piece_square.file, piece_square.rank + forward * 2)
    right_diagonal_square = Coordinate(piece_square.file + 1, piece_square.rank + forward)
    left_diagonal_square = Coordinate(piece_square.file - 1, piece_square.rank + forward)

    if game_state.board.square_is_empty(forward_square):
        result_without_promotion_moves.add(BasicMove(piece_square, forward_square))
        
        if piece_square.rank == second_rank and game_state.board.square_is_empty(double_forward_square):
            result_without_promotion_moves.add(PawnDoubleMove(piece_square, double_forward_square))

    if square_contains_color(game_state, right_diagonal_square, piece_color.opposite()):
        result_without_promotion_moves.add(BasicMove(piece_square, right_diagonal_square))

    if square_contains_color(game_state, left_diagonal_square, piece_color.opposite()):
        result_without_promotion_moves.add(BasicMove(piece_square, left_diagonal_square))

    if right_diagonal_square == game_state.en_passant_target_square:
        result_without_promotion_moves.add(EnPassantMove(piece_square, right_diagonal_square))
    elif left_diagonal_square == game_state.en_passant_target_square:
        result_without_promotion_moves.add(EnPassantMove(piece_square, left_diagonal_square))

    result_with_promotion_moves = set()

    for move in result_without_promotion_moves:
        if not isinstance(move, BasicMove):
            result_with_promotion_moves.add(move)
            continue

        if move.target_square.rank == eigth_rank:
            for piece_type in get_promotable_piece_types():
                result_with_promotion_moves.add(PromotionMove(move.source_square, move.target_square, piece_type))
        else:
            result_with_promotion_moves.add(move)

    return result_without_promotion_moves


def get_promotable_piece_types() -> Set[PieceType]:
    return set([
        PieceType.ROOK,
        PieceType.BISHOP,
        PieceType.KNIGHT,
        PieceType.QUEEN
    ])


def square_contains_color(game_state: GameState, piece_square: Coordinate, color: Color) -> bool:
    if not game_state.board.contains_square(piece_square):
        return False

    piece_at_square = game_state.board.at(piece_square)

    if piece_at_square is None:
        return False

    return piece_at_square.color == color


def get_forward_direction_for_color(color: Color) -> int:
    if color is Color.WHITE:
        return 1
    else:
        return -1


def filter_moves_evading_check(game_state: GameState, unfiltered_moves: Set[Move]) -> Set[Move]:
    result = set()

    for move in unfiltered_moves:
        if move_evades_check(game_state, move):
            result.add(move)

    return result

    
def move_evades_check(game_state: GameState, move: Move) -> bool:
    move_doer = get_move_doer(game_state, move)
    game_state_copy = deepcopy(game_state)
    do_move(game_state_copy, move)

    return not is_in_check(game_state_copy, move_doer)


def get_move_doer(game_state: GameState, move: Move) -> Color:
    if isinstance(move, CastlingMove):
        return move.color
    elif isinstance(move, BasicMove) or isinstance(move, EnPassantMove) or isinstance(move, PawnDoubleMove) or isinstance(move, PromotionMove):
        piece_at_source_square = game_state.board.at(move.source_square)

        if piece_at_source_square is None:
            raise ValueError("move source square is empty")

        return piece_at_source_square.color
    else:
        raise ValueError("invalid move type")


def is_in_check(game_state: GameState, color: Color):
    king_square = get_king_square(game_state, color)

    return square_is_threatened(game_state, king_square, color.opposite())


def get_king_square(game_state: GameState, color: Color):
    king_square = get_piece_square(game_state, Piece(color, PieceType.KING))

    if king_square is None:
        raise ValueError("king not found")

    return king_square


def get_piece_square(game_state: GameState, target_piece: Piece) -> Optional[Coordinate]:
    for rank, piece_row in enumerate(game_state.board.matrix):
        for file, piece in enumerate(piece_row):
            if piece == target_piece:
                return Coordinate(file, rank)

    return None


def square_is_threatened(game_state: GameState, square: Coordinate, threatening_color: Color):
    if square_next_to_king_of_color(game_state, square, threatening_color):
        return True

    for rank, piece_row in enumerate(game_state.board.matrix):
        for file, piece in enumerate(piece_row):
            if piece is None or piece.color is threatening_color.opposite() or piece.piece_type is PieceType.KING:
                continue

            piece_square = Coordinate(file, rank)
            if piece_threatens_square(game_state, piece_square, square):
                return True

    return False


def square_next_to_king_of_color(game_state: GameState, square: Coordinate, king_color: Color):
    king_square = get_king_square(game_state, king_color)
    squares_surrounding_king = get_surrounding_squares(game_state, king_square)

    return square in squares_surrounding_king


def get_surrounding_squares(game_state: GameState, square: Coordinate) -> Set[Coordinate]:
    offsets = set([
        Coordinate(-1, -1),
        Coordinate( 0, -1),
        Coordinate( 1, -1),
        Coordinate(-1,  0),
        Coordinate( 1,  0),
        Coordinate(-1,  1),
        Coordinate( 0,  1),
        Coordinate( 1,  1),
    ])
    
    offsetted_squares = apply_offsets_to_square(game_state, square, offsets)

    offsetted_squares_contained_by_board = filter_squares_contained_by_board(game_state.board, offsetted_squares)

    return offsetted_squares_contained_by_board


def apply_offsets_to_square(game_state: GameState, square: Coordinate, offsets: Set[Coordinate]) -> Set[Coordinate]:
    result = set()

    for offset in offsets:
        offsetted_square = square + offset

        if game_state.board.contains_square(offsetted_square):
            result.add(offsetted_square)

    return result


def filter_squares_contained_by_board(board: Board, unfiltered_squares: Set[Coordinate]) -> Set[Coordinate]:
    result = set()

    for square in unfiltered_squares:
        if board.contains_square(square):
            result.add(square)

    return result
    

def piece_threatens_square(game_state: GameState, piece_square: Coordinate, target_square: Coordinate) -> bool:
    for move in generate_moves_for_piece(game_state, piece_square, must_evade_check=False):
        if move_threatens_square(move, target_square):
            return True

    return False


def move_threatens_square(move: Move, square: Coordinate) -> bool:
    if isinstance(move, BasicMove):
        return move.target_square == square
    elif isinstance(move, EnPassantMove):
        return move.target_square == square
    else:
        return False


def do_move(game_state: GameState, move: Move) -> None:
    if isinstance(move, BasicMove):
        do_basic_move(game_state, move)
    elif isinstance(move, CastlingMove):
        do_castling_move(game_state, move)
    elif isinstance(move, EnPassantMove):
        do_en_passant_move(game_state, move)
    elif isinstance(move, PawnDoubleMove):
        do_pawn_double_move(game_state, move)
    elif isinstance(move, PromotionMove):
        do_promotion_move(game_state, move)
    else:
        raise ValueError("invalid move type")

    if game_state.color_to_move is Color.BLACK:
        game_state.fullmove_count += 1

    game_state.color_to_move = game_state.color_to_move.opposite()


def do_castling_move(game_state: GameState, move: CastlingMove) -> None:
    game_state.halfmove_clock += 1

    king_target_square = get_castling_king_target_square(move)
    rook_target_square = get_castling_rook_target_square(move)

    rook_source_square = get_castling_rook_square(move)
    king_source_square = get_castling_king_square(move)

    game_state.board.set_at(rook_source_square, None)
    game_state.board.set_at(king_source_square, None)

    game_state.board.set_at(king_target_square, Piece(move.color, PieceType.KING))
    game_state.board.set_at(rook_target_square, Piece(move.color, PieceType.ROOK))

    game_state.castling_permissions.set_can_castle_on_side(move.color, move.side, False)


def do_pawn_double_move(game_state: GameState, move: PawnDoubleMove) -> None:
    source_piece = game_state.board.at(move.source_square)

    if source_piece is None:
        raise ValueError("move.source_square is empty")

    game_state.board.set_at(move.source_square, None)
    game_state.board.set_at(move.target_square, source_piece)

    game_state.halfmove_clock = 0
    

def do_promotion_move(game_state: GameState, move: PromotionMove):
    source_piece = game_state.board.at(move.source_square)

    if source_piece is None:
        raise ValueError("move.source_square is empty")

    game_state.board.set_at(move.source_square, None)
    game_state.board.set_at(move.target_square, Piece(source_piece.color, move.promote_to))
    
    game_state.halfmove_clock = 0


def do_en_passant_move(game_state: GameState, move: EnPassantMove):
    source_piece = game_state.board.at(move.source_square)

    if source_piece is None:
        raise ValueError("move.source_square is empty")

    forward = get_forward_direction_for_color(source_piece.color)
    attacking_square = Coordinate(move.target_square.file, move.target_square.rank - forward)

    game_state.board.set_at(move.source_square, None)
    game_state.board.set_at(attacking_square, None)
    game_state.board.set_at(move.target_square, source_piece)

    game_state.halfmove_clock = 0


def do_basic_move(game_state: GameState, move: BasicMove):
    source_piece = game_state.board.at(move.source_square)
    target_piece = game_state.board.at(move.target_square)

    if source_piece is None:
        raise ValueError("move.source_square is empty")

    piece_color = source_piece.color

    if source_piece.piece_type == PieceType.KING:
        game_state.castling_permissions.disable_all_castling_for_color(piece_color)

    if target_piece is not None and target_piece.piece_type == PieceType.KING:
        game_state.castling_permissions.disable_all_castling_for_color(target_piece.color)

    kingside_castling_move = CastlingMove(CastlingSide.KINGSIDE, piece_color)
    queenside_castling_move = CastlingMove(CastlingSide.QUEENSIDE, piece_color)
    kingside_rook_square = get_castling_rook_square(kingside_castling_move)
    queenside_rook_square = get_castling_rook_square(queenside_castling_move)

    if move.source_square == kingside_rook_square:
        game_state.castling_permissions.set_can_castle_on_side(piece_color, CastlingSide.KINGSIDE, False)
    elif move.source_square == queenside_rook_square:
        game_state.castling_permissions.set_can_castle_on_side(piece_color, CastlingSide.QUEENSIDE, False)

    if move.target_square == kingside_rook_square:
        game_state.castling_permissions.set_can_castle_on_side(piece_color.opposite(), CastlingSide.KINGSIDE, False)
    elif move.target_square == queenside_rook_square:
        game_state.castling_permissions.set_can_castle_on_side(piece_color.opposite(), CastlingSide.QUEENSIDE, False)

    if target_piece is not None or source_piece.piece_type == PieceType.PAWN:
        game_state.halfmove_clock = 0
    else:
        game_state.halfmove_clock += 1

    game_state.board.set_at(move.source_square, None)
    game_state.board.set_at(move.target_square, source_piece)


def is_legal_move(game_state: GameState, move: Move):
    possible_moves = generate_moves(game_state)

    return move in possible_moves
