from user_input.user_input import input_sequence
from queue import Queue
from engine.engine import (
    verify_move,
    do_move,
    is_in_checkmate,
    square_contains_color,
    generate_moves_for_piece
)
from move import Move
import threading
import pygame
import sys
from piece import Piece
from typing import Tuple, Set, Optional
from math import ceil
from coordinate import Coordinate
from piece_tilemap import get_piece_image
from engine.castling_squares import get_castling_king_target_square
from move import (
    Move,
    CastlingMove,
    PawnDoubleMove,
    PromotionMove,
    EnPassantMove,
    BasicMove
)


INITIAL_WINDOW_DIMENSIONS = (600, 600)


pygame.init()
game_state, client_color, connection = input_sequence()
game_state_lock = threading.Lock()
move_queue = Queue(maxsize=1)


def verify_and_do_move(move: Move):
    with game_state_lock:
        if not verify_move(game_state, move):
            raise ValueError("illegal move")

        do_move(game_state, move)


def play_client_move():
    move = move_queue.get()
    connection.send_move(move)

    verify_and_do_move(move)


def play_opponent_move():
    move = connection.receive_move()

    verify_and_do_move(move)


def business_logic():
    while True:
        if is_in_checkmate(game_state):
            raise ValueError("checkmate")

        if game_state.color_to_move is client_color:
            play_client_move()
        else:
            play_opponent_move()


business_logic_thread = threading.Thread(target=business_logic)
business_logic_thread.start()


# possible_moves_for_selected_piece: Optional[Set[Move]] = set([BasicMove(Coordinate(0, 0), Coordinate(0, 4))])
# mouse_offset: Optional[Tuple[int, int]] = (0, 0)
# selected_piece_square = Coordinate(0, 0)
possible_moves_for_selected_piece: Optional[Set[Move]] = None
mouse_offset: Optional[Tuple[int, int]] = None
selected_piece_square = None


def get_chessboard_rect(window_dimensions: Tuple[int, int]) -> pygame.rect.Rect:
    window_width, window_height = window_dimensions
    shorter_side = min(window_width, window_height)

    padding_left = ceil((window_width - shorter_side) * 0.5)
    padding_top = ceil((window_height - shorter_side) * 0.5)

    return pygame.rect.Rect(padding_left, padding_top, shorter_side, shorter_side)


def get_square_rect(chessboard_rect: pygame.rect.Rect, square: Coordinate) -> pygame.rect.Rect:
    _, _, chessboard_size, _ = chessboard_rect

    square_size = ceil(get_square_size(chessboard_size))
    square_pos = get_square_position(chessboard_rect, square)

    square_position_x, square_position_y = square_pos
    
    return pygame.rect.Rect(square_position_x, square_position_y, square_size, square_size)


def get_square_position(chessboard_rect: pygame.rect.Rect, square: Coordinate):
    padding_left, padding_top, chessboard_size, _ = chessboard_rect
    square_size = get_square_size(chessboard_size)

    offset_x = square_size * square.file
    offset_y = square_size * (7 - square.rank)

    return (padding_left + offset_x, padding_top + offset_y)


def get_square_size(chessboard_size: int) -> float:
    square_size = chessboard_size / 8

    return square_size


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


def possible_moves_for_selected_piece_include_square(square: Coordinate) -> bool:
    if possible_moves_for_selected_piece is None:
        return False
    
    for move in possible_moves_for_selected_piece:
        signature_square = get_move_signature_square(move)

        if signature_square == square:
            return True

    return False


def get_color_for_square(square: Coordinate) -> pygame.color.Color:
    # TODO: slightly adjust colors when mouse is hovering over square
    if possible_moves_for_selected_piece_include_square(square):
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


def draw_chessboard(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect) -> None:
    with game_state_lock:
        for rank_index in range(8):
            for file_index in range(8):
                square = Coordinate(rank_index, file_index)
                square_color = get_color_for_square(square)
                square_rect = get_square_rect(chessboard_rect, square)
                pygame.draw.rect(surface, square_color, square_rect)

                if square == selected_piece_square:
                    continue

                piece_at_square = game_state.board.at(square)

                if piece_at_square is None:
                    continue

                draw_piece_at_square(surface, chessboard_rect, piece_at_square, square)

            draw_selected_piece(surface, chessboard_rect)


def draw_selected_piece(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect):
    if selected_piece_square is not None and mouse_offset is not None:
        _, _, chessboard_size, _ = chessboard_rect
        square_size = ceil(get_square_size(chessboard_size))
        piece = game_state.board.at(selected_piece_square)

        if piece is None:
            raise ValueError("empty square")

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_offset_x, mouse_offset_y = mouse_offset
        piece_rect = pygame.rect.Rect(mouse_x - mouse_offset_x, mouse_y - mouse_offset_y, square_size, square_size)

        draw_piece_at_rect(surface, piece, piece_rect)


def on_mouse_button_down(chessboard_rect: pygame.rect.Rect) -> None:
    with game_state_lock:
        global selected_piece_square
        global mouse_offset
        global possible_moves_for_selected_piece

        square_under_mouse, offset = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos())

        if game_state.color_to_move is not client_color:
            return

        if not square_contains_color(game_state, square_under_mouse, game_state.color_to_move):
            return

        selected_piece_square = square_under_mouse
        mouse_offset = offset
        possible_moves_for_selected_piece = generate_moves_for_piece(game_state, square_under_mouse)

    
def get_square_on_board_and_offset_for_position(chessboard_rect: pygame.rect.Rect, position: Tuple[int, int]) -> Tuple[Coordinate, Tuple[int, int]]:
    chessboard_padding_x, chessboard_padding_y, chessboard_size, _ = chessboard_rect
    square_size = get_square_size(chessboard_size)

    position_x, position_y = position

    relative_position_x = position_x - chessboard_padding_x
    relative_position_y = position_y - chessboard_padding_y

    square_x = int(relative_position_x // square_size)
    square_y = int(relative_position_y // square_size)
    offset_x = int(relative_position_x % square_size)
    offset_y = int(relative_position_y % square_size)

    return Coordinate(square_x, 7 - square_y), (offset_x, offset_y)


def get_possible_move_with_signature_square(square: Coordinate) -> Optional[Move]:
    if possible_moves_for_selected_piece is None:
        return None

    for move in possible_moves_for_selected_piece:
        if get_move_signature_square(move) == square:
            return move

    return None


def on_mouse_button_up(chessboard_rect: pygame.rect.Rect) -> None:
    with game_state_lock:
        global selected_piece_square
        global mouse_offset
        global possible_moves_for_selected_piece

        square_under_mouse, _ = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos())

        move = get_possible_move_with_signature_square(square_under_mouse)

        if move is not None:
            # TODO: handle promotion moves separately
            move_queue.put(move)


        selected_piece_square = None
        mouse_offset = None
        possible_moves_for_selected_piece = None


def render_logic():
    window = pygame.display.set_mode(INITIAL_WINDOW_DIMENSIONS, pygame.RESIZABLE)

    while True:
        chessboard_rect = get_chessboard_rect(window.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    on_mouse_button_down(chessboard_rect)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    on_mouse_button_up(chessboard_rect)
                

        window.fill((0, 0, 0))
        draw_chessboard(window, chessboard_rect)

        pygame.display.update()

render_logic_thread = threading.Thread(target=render_logic)
render_logic_thread.start()
