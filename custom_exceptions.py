class InvalidFenString(ValueError):
    pass


class InvalidPieceString(InvalidFenString):

    def __init__(self, char=None):
        self.char = char


class InvalidColorString(InvalidFenString):
    pass


class InvalidHalfmoveString(InvalidFenString):
    pass


class InvalidFullmoveString(InvalidFenString):
    pass
