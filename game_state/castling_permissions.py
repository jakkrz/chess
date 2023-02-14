from color import Color
from dataclasses import dataclass

@dataclass
class PlayerCastlingPermissions:
    can_kingside: bool = True
    can_queenside: bool = True


class GlobalCastlingPermissions:

    def __init__(self):
        self.white_castling_perms = PlayerCastlingPermissions()
        self.black_castling_perms = PlayerCastlingPermissions()

    def get_castling_perms(self, color) -> PlayerCastlingPermissions:
        if color is Color.WHITE:
            return self.white_castling_perms
        else:
            return self.black_castling_perms

    def can_castle_kingside(self, color) -> bool:
        return self.get_castling_perms(color).can_kingside

    def can_castle_queenside(self, color) -> bool:
        return self.get_castling_perms(color).can_queenside

    def enable_castle_kingside(self, color):
        self.get_castling_perms(color).can_kingside = True

    def enable_castle_queenside(self, color):
        self.get_castling_perms(color).can_queenside = True

    def disable_castle_kingside(self, color):
        self.get_castling_perms(color).can_kingside = False

    def disable_castle_queenside(self, color):
        self.get_castling_perms(color).can_queenside = False

    def disable_all_castling(self):
        self.disable_castle_kingside(Color.WHITE)
        self.disable_castle_queenside(Color.WHITE)
        self.disable_castle_kingside(Color.BLACK)
        self.disable_castle_queenside(Color.BLACK)
