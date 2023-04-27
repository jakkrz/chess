import pytest
from parsing.fen_parser import FenParser

@pytest.fixture
def fen_parser():
    return FenParser()

@pytest.mark.parametrize("fen_string", [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
])
def test_serialize_is_inverse_of_parse(fen_string: str, fen_parser: FenParser):
    assert fen_parser.serialize(fen_parser.parse(fen_string))

