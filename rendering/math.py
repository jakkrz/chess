from math import ceil
from typing import Tuple
from coordinate import Coordinate
import pygame


def get_chessboard_rect(window_dimensions: Tuple[int, int]) -> pygame.rect.Rect:
    window_width, window_height = window_dimensions
    chessboard_size = get_chessboard_size(window_dimensions)

    padding_left = ceil((window_width - chessboard_size) * 0.5)
    padding_top = ceil((window_height - chessboard_size) * 0.5)

    return pygame.rect.Rect(padding_left, padding_top, chessboard_size, chessboard_size)


def get_chessboard_size(window_dimensions: Tuple[int, int]) -> int:
    window_width, window_height = window_dimensions
    return min(window_width, window_height)


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
