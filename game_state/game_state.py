from color import Color
from game_state.board import Board
from game_state.castling_permissions import CastlingPermissions
from typing import Union
from coordinate import Coordinate

class GameState:
    def __init__(self):
        self.board = Board()
        self.color_to_move = Color.WHITE
        self.castling_permissions = CastlingPermissions()
        self.en_passant_target_square: Union[None, Coordinate] = None
        self.halfmove_clock = 0
        self.fullmove_count = 0
