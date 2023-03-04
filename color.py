from enum import Enum, auto


class Color(Enum):
    WHITE = auto()
    BLACK = auto()

    def opposite(self) -> "Color":
        if self is Color.WHITE:
            return Color.BLACK
        else:
            return Color.WHITE
        

