from color import Color


class PlayerCastlingPermissions:

    def __init__(self, can_kingside=True, can_queenside=True):
        self.can_kingside = can_kingside
        self.can_queenside = can_queenside


class GlobalCastlingPermissions:

    def __init__(self):
        self.white_castling_perms = PlayerCastlingPermissions()
        self.black_castling_perms = PlayerCastlingPermissions()

    def get_castling_perms(self, color):
        if color is Color.WHITE:
            return self.white_castling_perms
        else:
            return self.black_castling_perms

    def can_castle_kingside(self, color):
        return self.get_castling_perms(color).can_kingside

    def can_castle_queenside(self, color):
        return self.get_castling_perms(color).can_queenside

    def disable_castle_kingside(self, color):
        self.get_castling_perms(color).kingside = False

    def disable_castle_queenside(self, color):
        self.get_castling_perms(color).queenside = False

    def disable_all_castling(self):
        self.disable_castle_kingside(Color.WHITE)
        self.disable_castle_queenside(Color.WHITE)
        self.disable_castle_kingside(Color.BLACK)
        self.disable_castle_queenside(Color.BLACK)
