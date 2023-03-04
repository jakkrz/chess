from piece import Piece, PieceType
from color import Color
from typing import List, Optional
from coordinate import Coordinate

_emoji_mapping = {
    Piece(Color.BLACK, PieceType.KING): "♔",
    Piece(Color.BLACK, PieceType.QUEEN): "♕",
    Piece(Color.BLACK, PieceType.ROOK): "♖",
    Piece(Color.BLACK, PieceType.BISHOP): "♗",
    Piece(Color.BLACK, PieceType.KNIGHT): "♘",
    Piece(Color.BLACK, PieceType.PAWN): "♙",
    Piece(Color.WHITE, PieceType.KING): "♚",
    Piece(Color.WHITE, PieceType.QUEEN): "♛",
    Piece(Color.WHITE, PieceType.ROOK): "♜",
    Piece(Color.WHITE, PieceType.BISHOP): "♝",
    Piece(Color.WHITE, PieceType.KNIGHT): "♞",
    Piece(Color.WHITE, PieceType.PAWN): "♟︎",
}

BoardMatrix = List[List[Optional[Piece]]]


def create_matrix(files, ranks) -> BoardMatrix:
    result = []

    for _ in range(ranks):
        result.append([None] * files)

    return result


class Board:

    def __init__(self, matrix: Optional[BoardMatrix] = None):
        if matrix is None:
            matrix = create_matrix(8, 8)

        self.matrix = matrix

    def at(self, coordinate: Coordinate) -> Optional[Piece]:
        return self.matrix[coordinate.rank][coordinate.file]

    def __repr__(self) -> str:
        result = ""

        for rank in self.matrix[::-1]:
            for piece in rank:
                if piece is None:
                    result += ". "
                    continue

                result += _emoji_mapping[piece] + " "

            result += "\n"

        return result

    def square_is_empty(self, coordinate: Coordinate) -> bool:
        return self.at(coordinate) is None

    def get_nth_rank_for_color(self, n: int, color: Color) -> int:
        if color is Color.WHITE:
            return -1 + n
        else:
            return 8 - n

    def contains_square(self, square: Coordinate) -> bool:
        return 0 <= square.file <= 7 and 0 <= square.rank <= 7
