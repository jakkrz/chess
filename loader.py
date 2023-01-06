from piece import Piece, PieceType


def read_file(filename):
    with open(filename, "r") as f:
        return f.readlines()


key = {
    "p": PieceType.PAWN,
    "k": PieceType.KING,
    "h": PieceType.HORSE,
    "c": PieceType.CASTLE,
    "b": PieceType.BISHOP,
    "q": PieceType.QUEEN,
}


def load_board_from_file(filename):
    board = []

    for line in read_file(filename):
        line_in_board = []
        line = line.removesuffix("\n")

        for word in line.split(" "):
            if word == "e":
                line_in_board.append(None)
                continue

            line_in_board.append(Piece(word.isupper(), key[word.lower()]))

        board.append(line_in_board)

    return board
