from engine.engine import (
    square_contains_color,
    generate_moves_for_piece,
    get_promotable_piece_types
)

from environment import Environment
from rendering.math import (
    get_chessboard_rect,
    get_chessboard_size,
    get_square_rect,
    get_square_size,
    get_square_on_board_and_offset_for_position
)
from color import Color
from rendering.selection import Selection
from move import Move
import pygame
from copy import deepcopy
from piece import Piece, PieceType
from typing import Set, Optional, Tuple
from math import floor, ceil
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


def draw_piece_at_square(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect, piece: Piece, square: Coordinate, flip: bool):
    square_rect = get_square_rect(chessboard_rect, square, flip)

    draw_piece_at_rect(surface, piece, square_rect)


def draw_piece_at_rect(surface: pygame.surface.Surface, piece: Piece, piece_rect: pygame.rect.Rect):
    piece_image = get_piece_image(piece)
    piece_position_x, piece_position_y, piece_width, piece_height = piece_rect

    surface.blit(pygame.transform.scale(piece_image, (piece_width, piece_height)), (piece_position_x, piece_position_y))


def draw_chessboard(surface: pygame.surface.Surface, chessboard_rect: pygame.rect.Rect, environment: Environment, selection: Optional[Selection], flip: bool) -> None:
    with environment.game_state_lock:
        for rank_index in range(8):
            for file_index in range(8):
                square = Coordinate(rank_index, file_index)
                square_color = get_color_for_square(selection, square)
                square_rect = get_square_rect(chessboard_rect, square, flip)
                pygame.draw.rect(surface, square_color, square_rect)

                if selection is not None and square == selection.selected_piece_square:
                    continue

                piece_at_square = environment.game_state.board.at(square)

                if piece_at_square is None:
                    continue

                draw_piece_at_square(surface, chessboard_rect, piece_at_square, square, flip)

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


def on_selection_start(environment: Environment, chessboard_rect: pygame.rect.Rect, flip: bool) -> Optional[Selection]:
    with environment.game_state_lock:
        game_state = environment.game_state

        square_under_mouse, offset = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos(), flip)

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


def on_selection_end(environment: Environment, chessboard_rect: pygame.rect.Rect, selection: Selection, flip: bool) -> Optional[PromotionMove]:
    if selection is not None:
        square_under_mouse, _ = get_square_on_board_and_offset_for_position(chessboard_rect, pygame.mouse.get_pos(), flip)

        move = get_possible_move_with_signature_square(selection.possible_moves_for_selected_piece, square_under_mouse)

        if move is not None:
            if isinstance(move, PromotionMove):
                return move
            else:
                environment.move_queue.put(move)


PROMOTION_MENU_PADDING_FACTOR = 0.1


def get_promotion_menu_size(surface: pygame.surface.Surface) -> Tuple[int, int]:
    promotable_piece_type_count = len(get_promotable_piece_types())
    chessboard_size = get_chessboard_size(surface.get_size())
    square_size = get_square_size(chessboard_size)

    padding = square_size * PROMOTION_MENU_PADDING_FACTOR
    padding_both_sides = padding * 2

    width = floor(square_size + padding_both_sides)
    height = floor(promotable_piece_type_count * square_size + padding_both_sides)

    return (width, height)
    

def get_promotion_menu_rect(surface: pygame.surface.Surface, promotion_move_target_square: Coordinate, flip: bool) -> pygame.rect.Rect:
    promotion_menu_width, promotion_menu_height = get_promotion_menu_size(surface)

    chessboard_rect = get_chessboard_rect(surface.get_size())
    target_square_x, target_square_y, square_size, _ = get_square_rect(chessboard_rect, promotion_move_target_square, flip)
    padding = square_size * PROMOTION_MENU_PADDING_FACTOR

    promotion_menu_position_x = target_square_x - padding
    promotion_menu_position_y = target_square_y - padding

    return pygame.rect.Rect(promotion_menu_position_x, promotion_menu_position_y, promotion_menu_width, promotion_menu_height)


def get_promotion_menu_piece_rect_by_number(surface: pygame.surface.Surface, promotion_move_target_square: Coordinate, number: int, flip: bool) -> pygame.rect.Rect:
    chessboard_rect = get_chessboard_rect(surface.get_size())
    target_square_x, target_square_y, square_size, _ = get_square_rect(chessboard_rect, promotion_move_target_square, flip)
    chessboard_size = get_chessboard_size(surface.get_size())
    square_size = get_square_size(chessboard_size)

    piece_rect_y = target_square_y + square_size * number

    return pygame.rect.Rect(target_square_x, piece_rect_y, square_size, square_size)


PROMOTION_MENU_PIECE_TYPE_ORDER = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]

    
def get_promotion_menu_piece_rect(surface: pygame.surface.Surface, promotion_move_target_square: Coordinate, piece_type: PieceType, flip: bool) -> pygame.rect.Rect:
    piece_type_index = PROMOTION_MENU_PIECE_TYPE_ORDER.index(piece_type)

    return get_promotion_menu_piece_rect_by_number(surface, promotion_move_target_square, piece_type_index, flip)


def draw_promotion_menu_frame(surface: pygame.surface.Surface, promotion_move_target_square: Coordinate, flip: bool) -> None:
    promotion_menu_rect = get_promotion_menu_rect(surface, promotion_move_target_square, flip)

    pygame.draw.rect(surface, PROMOTION_MENU_COLOR, promotion_menu_rect, border_radius=PROMOTION_MENU_BORDER_RADIUS)


PROMOTION_MENU_COLOR = pygame.color.Color(255, 255, 255)
PROMOTION_MENU_HIGHLIGHT_COLOR = pygame.color.Color(200, 200, 200)
PROMOTION_MENU_BORDER_RADIUS = 5


def draw_promotion_menu_piece(surface: pygame.surface.Surface, promotion_move_target_square: Coordinate, piece: Piece, flip: bool) -> None:
    piece_rect = get_promotion_menu_piece_rect(surface, promotion_move_target_square, piece.piece_type, flip)
    
    mouse_pos = pygame.mouse.get_pos()
    if piece_rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, PROMOTION_MENU_HIGHLIGHT_COLOR, piece_rect)

    draw_piece_at_rect(surface, piece, piece_rect)



def draw_promotion_menu(surface: pygame.surface.Surface, client_color: Color, promotion_move: PromotionMove, flip: bool):
    promotable_piece_types = get_promotable_piece_types()    
    
    draw_promotion_menu_frame(surface, promotion_move.target_square, flip)

    for piece_type in promotable_piece_types:
        draw_promotion_menu_piece(surface, promotion_move.target_square, Piece(client_color, piece_type), flip)


def copy_promotion_move_with_new_piece_type(promotion_move: PromotionMove, new_piece_type: PieceType):
    new_promotion_move = deepcopy(promotion_move)
    new_promotion_move.promote_to = new_piece_type

    return new_promotion_move


def handle_promotion_menu_click(surface: pygame.surface.Surface, environment: Environment, promotion_move: PromotionMove, flip: bool):
    mouse_pos = pygame.mouse.get_pos()
    promotable_piece_types = get_promotable_piece_types()

    for piece_type in promotable_piece_types:
        piece_rect = get_promotion_menu_piece_rect(surface, promotion_move.target_square, piece_type, flip)

        if piece_rect.collidepoint(mouse_pos):
            new_promotion_move = copy_promotion_move_with_new_piece_type(promotion_move, piece_type)
            environment.move_queue.put(new_promotion_move)

            break
            
    


def render_logic(environment: Environment):
    window = pygame.display.set_mode(INITIAL_WINDOW_DIMENSIONS, pygame.RESIZABLE)
    selection: Optional[Selection] = None
    current_promotion_move: Optional[PromotionMove] = None
    flip = environment.client_color == Color.BLACK

    while True:
        chessboard_rect = get_chessboard_rect(window.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                environment.close_event.set()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not current_promotion_move:
                        selection = on_selection_start(environment, chessboard_rect, flip)
                    else:
                        handle_promotion_menu_click(window, environment, current_promotion_move, flip)
                        current_promotion_move = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if selection is not None:
                        current_promotion_move = on_selection_end(environment, chessboard_rect, selection, flip)

                    selection = None
                
        window.fill((0, 0, 0))
        draw_chessboard(window, chessboard_rect, environment, selection, flip)

        if current_promotion_move is not None:
            draw_promotion_menu(window, environment.client_color, current_promotion_move, flip)

        pygame.display.update()

