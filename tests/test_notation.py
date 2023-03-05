import pytest
from piece import Piece, PieceType
from color import Color
import notation

@pytest.mark.parametrize("piece,char", [
    (Piece(Color.WHITE, PieceType.KING), "K"),
    (Piece(Color.WHITE, PieceType.QUEEN), "Q"),
    (Piece(Color.WHITE, PieceType.KNIGHT), "N"),
    (Piece(Color.WHITE, PieceType.ROOK), "R"),
    (Piece(Color.WHITE, PieceType.BISHOP), "B"),
    (Piece(Color.WHITE, PieceType.PAWN), "P"),
    (Piece(Color.BLACK, PieceType.KING), "k"),
    (Piece(Color.BLACK, PieceType.QUEEN), "q"),
    (Piece(Color.BLACK, PieceType.KNIGHT), "n"),
    (Piece(Color.BLACK, PieceType.ROOK), "r"),
    (Piece(Color.BLACK, PieceType.BISHOP), "b"),
    (Piece(Color.BLACK, PieceType.PAWN), "p"),
])
class TestPieceCharacterConversion:
    def test_get_piece_by_character(self, piece: Piece, char: str):
        assert notation.get_piece_by_character(char) == piece

    def test_character_to_piece(self, piece: Piece, char: str):
        assert notation.get_character_by_piece(piece) == char

