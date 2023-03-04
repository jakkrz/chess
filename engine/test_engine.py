import unittest
from engine.engine import verify_basic_move

from move import (
    BasicMove,
    CastlingMove,
    EnPassantMove,
    PawnDoubleMove,
    PromotionMove
)
from files import load_default_game

class TestVerify:
    def test_basic_move(self):
        game_state = load_default_game()
        self.assertEqual()
        
