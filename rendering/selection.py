from dataclasses import dataclass
from typing import Set, Tuple
from move import Move
from coordinate import Coordinate

@dataclass
class Selection:
    selected_piece_square: Coordinate
    mouse_offset: Tuple[int, int]
    possible_moves_for_selected_piece: Set[Move]
    
