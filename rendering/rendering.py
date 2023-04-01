from engine.engine import (
    square_contains_color,
    generate_moves_for_piece
)

from environment import Environment
from rendering.math import (
    get_chessboard_rect,
    get_square_rect,
    get_square_size,
    get_square_on_board_and_offset_for_position
)
from rendering.selection import Selection
from move import Move
import pygame
from piece import Piece
from typing import Set, Optional
from math import ceil
from coordinate import Coordinate
from rendering.tilemap import get_piece_image
from engine.castling_squares import get_castling_king_target_square
from game_state.game_state import GameState
from move import (
    Move,
    CastlingMove,
    PawnDoubleMove,
    PromotionMove,
    EnPassantMove,
    BasicMove
)


INITIAL_WINDOW_DIMENSIONS = (600, 600)


def square_is_white(square: Coordinate):
    return (square.file + square.rank) % 2 != 0


def get_square_white_or_black_color(square: Coordinate) -> pygame.color.Color:
    if square_is_white(square):
        return pygame.color.Color(180, 180, 180)
    else:
        return pygame.color.Color(100, 100, 100)


def get_move_signature_square(move: Move) -> Coordinate:
    if isinstance(move, CastlingMove):
        return get_castling_king_target_square(move)
    elif isinstance(move, BasicMove) or isinstance(move, PawnDoubleMove) or isinstance(move, PromotionMove) or isinstance(move, EnPassantMove):
        return move.target_square
    else:
        raise ValueError("invalid move type")


def possible_moves_for_selected_piece_include_square(selection: Optional[Selection], square: Coordinate) -> bool:
    if selection is None:
        return False
    
    for move in selection.possible_moves_for_selected_piece:
        signature_square = get_move_signature_square(move)

        if signature_square == square:
            return True

    return False


def get_color_for_square(selection: Optional[Selection], square: Coordinate) -> pygame.color.Color:
    if possible_moves_for_selected_piece_include_square(selection, square):
        return pygame.color.Color(14, 204, 65)

    white_or_black_color = get_square_white_or_black_color(square)


    return white_or_black_color


def draw_piece_at_square(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect, piece: Piece, square: Coordinate):
    square_rect = get_square_rect(chessboard_rect, square)    

    draw_piece_at_rect(surface, piece, square_rect)


def draw_piece_at_rect(surface: pygame.surface.Surface, piece: Piece, piece_rect: pygame.rect.Rect):
    piece_image = get_piece_image(piece)
    piece_position_x, piece_position_y, piece_width, piece_height = piece_rect

    surface.blit(pygame.transform.scale(piece_image, (piece_width, piece_height)), (piece_position_x, piece_position_y))


def draw_chessboard(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect, environment: Environment, selection: Optional[Selection]) -> None:
    with environment.game_state_lock:
        for rank_index in range(8):
            for file_index in range(8):
                square = Coordinate(rank_index, file_index)
                square_color = get_color_for_square(selection, square)
                square_rect = get_square_rect(chessboard_rect, square)
                pygame.draw.rect(surface, square_color, square_rect)

                if selection is not None and square == selection.selected_piece_square:
                    continue

                piece_at_square = environment.game_state.board.at(square)

                if piece_at_square is None:
                    continue

                draw_piece_at_square(surface, chessboard_rect, piece_at_square, square)

        if selection is not None:
            draw_selected_piece(surface, environment.game_state, chessboard_rect, selection)


def draw_selected_piece(surface: pygame.surface.Surface, game_state: GameState, chessboard_rect: pygame.rect.Rect, selection: Selection):
    _, _, chessboard_size, _ = chessboard_rect
    square_size = ceil(get_square_size(chessboard_size))
    piece = game_state.board.at(selection.selected_piece_square)

    if piece is None:
        raise ValueError("empty square")

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_offset_x, mouse_offset_y = selection.mouse_offset
    piece_rect = pygame.rect.Rect(mouse_x - mouse_offset_x, mouse_y - mouse_offset_y, square_size, square_size)

    draw_piece_at_rect(surface, piece, piece_rect)


def on_selection_start(environment: Environment, chessboard_rect: pygame.rect.Rect) -> Optional[Selection]:
    with environment.game_state_lock:
        game_state = environment.game_state

        square_under_mouse, offset = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos())

        if game_state.color_to_move is not environment.client_color:
            return None

        if not square_contains_color(game_state, square_under_mouse, environment.game_state.color_to_move):
            return None

        possible_moves_for_selected_piece = generate_moves_for_piece(game_state, square_under_mouse) 
        return Selection(square_under_mouse, offset, possible_moves_for_selected_piece)

    

def get_possible_move_with_signature_square(moves: Set[Move], square: Coordinate) -> Optional[Move]:
    for move in moves:
        if get_move_signature_square(move) == square:
            return move

    return None


def on_selection_end(environment: Environment, chessboard_rect: pygame.rect.Rect, selection: Selection) -> None:
    if selection is not None:
        square_under_mouse, _ = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos())

        move = get_possible_move_with_signature_square(selection.possible_moves_for_selected_piece, square_under_mouse)

        if move is not None:
            # TODO: handle promotion moves separately
            environment.move_queue.put(move)


def render_logic(environment: Environment):
    window = pygame.display.set_mode(INITIAL_WINDOW_DIMENSIONS, pygame.RESIZABLE)
    selection: Optional[Selection] = None

    while True:
        chessboard_rect = get_chessboard_rect(window.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                environment.close_event.set()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selection = on_selection_start(environment, chessboard_rect)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if selection is not None:
                        on_selection_end(environment, chessboard_rect, selection)

                    selection = None
                
        window.fill((0, 0, 0))
        draw_chessboard(window, chessboard_rect, environment, selection)

        pygame.display.update()

