import pygame
from piece import Piece, PieceType
from typing import Tuple
from color import Color


PIECE_TYPE_X_INDICES = {
    PieceType.KING: 0,
    PieceType.QUEEN: 1,
    PieceType.BISHOP: 2,
    PieceType.KNIGHT: 3,
    PieceType.ROOK: 4,
    PieceType.PAWN: 5
}

COLOR_Y_INDICES = {
    Color.WHITE: 0,
    Color.BLACK: 1
}

TILEMAP_COLUMNS = 6
TILEMAP_ROWS = 2


def get_piece_image(piece: Piece) -> pygame.surface.Surface:
    x_index, y_index = get_piece_tilemap_indices(piece)
    return get_piece_image_at_index(x_index, y_index)


def get_piece_tilemap_indices(piece: Piece) -> Tuple[int, int]:
    x_index = PIECE_TYPE_X_INDICES[piece.piece_type]
    y_index = COLOR_Y_INDICES[piece.color]

    return x_index, y_index


PIECE_TILEMAP = pygame.image.load("pieces.png")


def get_piece_image_at_index(x_index: int, y_index: int) -> pygame.surface.Surface:
    piece_tilemap_width, piece_tilemap_height = PIECE_TILEMAP.get_size()

    piece_image_width = piece_tilemap_width / TILEMAP_COLUMNS
    piece_image_height = piece_tilemap_height / TILEMAP_ROWS

    piece_image_x_offset = piece_image_width * x_index
    piece_image_y_offset = piece_image_height * y_index

    result_surface = pygame.surface.Surface((int(piece_image_width), int(piece_image_height)), pygame.SRCALPHA, 32)
    result_surface.blit(PIECE_TILEMAP, (-piece_image_x_offset, -piece_image_y_offset))

    return result_surface
