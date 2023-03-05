from coordinate import Coordinate
from color import Color
from castling_side import CastlingSide

def get_castling_king_square(move: CastlingMove) -> Coordinate:
    if move.color is Color.WHITE:
        return Coordinate.from_string("e1")
    else:
        return Coordinate.from_string("e8")


def get_castling_rook_square(move: CastlingMove) -> Coordinate:
    if move.side is CastlingSide.KINGSIDE:
        rook_file = notation.get_file_by_char("h")
    else:
        rook_file = notation.get_file_by_char("a")

    if move.color is Color.WHITE:
        rook_rank = notation.get_rank_by_char("1")
    else:
        rook_rank = notation.get_rank_by_char("8")

    return Coordinate(rook_file, rook_rank)


def get_castling_target_square(move: CastlingMove) -> Coordinate:
    if move.side is CastlingSide.KINGSIDE:
        rook_file = notation.get_file_by_char("g")
    else:
        rook_file = notation.get_file_by_char("c")

    if move.color is Color.WHITE:
        rook_rank = notation.get_rank_by_char("1")
    else:
        rook_rank = notation.get_rank_by_char("8")

    return Coordinate(rook_file, rook_rank)


def _get_numbers_between(a: int, b: int) -> List[int]:
    if a < b:
        return list(range(a + 1, b))
    else:
        return list(range(a - 1, b, -1))


def get_intermediary_squares(square_a: Coordinate, square_b: Coordinate) -> List[Coordinate]:
    if square_a.rank == square_b.rank:
        intermediary_files = _get_numbers_between(square_a.file, square_b.file)

        return [Coordinate(file, square_a.rank) for file in intermediary_files]
    elif square_a.file == square_b.file:
        intermediary_ranks = _get_numbers_between(square_a.rank, square_b.rank)

        return [Coordinate(square_a.file, rank) for rank in intermediary_ranks]
    else:
        raise ValueError("Cannot get intermediary squares: square_a and square_b don't share file nor rank.")


def get_castling_intermediary_squares(move: CastlingMove) -> List[Coordinate]:
    king_square = get_castling_king_square(move)
    rook_square = get_castling_rook_square(move)

    return get_intermediary_squares(king_square, rook_square)


def get_castling_passthrough_squares(move: CastlingMove) -> List[Coordinate]:
    king_square = get_castling_king_square(move)
    target_square = get_castling_target_square(move)

    return get_intermediary_squares(king_square, target_square)
