import unittest
from parser.fen_parser import FenParser

fen_a = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
fen_b = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
fen_c = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
fen_d = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"


class TestFenParser(unittest.TestCase):

    def test_parse_encode(self):
        encoder = FenParser()

        self.assertEqual(encoder.serialize(encoder.parse(fen_a)), fen_a)
        self.assertEqual(encoder.serialize(encoder.parse(fen_b)), fen_b)
        self.assertEqual(encoder.serialize(encoder.parse(fen_c)), fen_c)
        self.assertEqual(encoder.serialize(encoder.parse(fen_d)), fen_d)
