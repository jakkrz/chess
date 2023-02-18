from custom_exceptions import (InvalidColorString,
                               InvalidHalfmoveString, InvalidFullmoveString)
from game_state.castling_permissions import CastlingPermissions
from game_state.game_state import GameState
from piece import PieceType
from color import Color
from game_state.board import Board
from coordinate import Coordinate
import notation


class FenParser:

    def parse(self, string: str):
        result = GameState()
        fields = self._split_into_fields(string)
        result.board = self._parse_board(fields[0])
        result.color_to_move = self._get_color_to_move(fields[1])

        result.castling_permissions = CastlingPermissions.from_string(fields[2])

        en_passant_target = self._get_en_passant_target_square(fields[3])
        result.en_passant_target_square = en_passant_target
        result.halfmove_clock = self._get_halfmove_clock(fields[4])
        result.fullmove_count = self._get_fullmove_count(fields[5])

        return result

    def _split_into_fields(self, content):
        return content.split(" ")

    def _parse_board(self, board_string):
        rank_strings = self._split_into_ranks(board_string)
        board = Board()

        for i, rank_string in enumerate(rank_strings):
            self._populate_board_rank_by_string(board.matrix[i], rank_string)

        # we reverse to make the board indexing order consistent
        # with how coordinates are given in chess

        board.matrix = board.matrix[::-1]

        return board

    def _split_into_ranks(self, board_string):
        return board_string.split("/")

    def _populate_board_rank_by_string(self, rank, string):
        file = 0

        for character in string:
            if character.isnumeric():
                files_to_skip = int(character)
                file += files_to_skip
                continue

            piece = notation.get_piece_by_character(character)
            rank[file] = piece
            file += 1


    def _get_color_to_move(self, string):
        if string == "w":
            return Color.WHITE
        elif string == "b":
            return Color.BLACK
        else:
            raise InvalidColorString


    def _get_en_passant_target_square(self, string):
        if string == "-":
            return None

        return Coordinate.from_string(string)

    def _get_halfmove_clock(self, string):
        try:
            return int(string)
        except ValueError:
            raise InvalidHalfmoveString

    def _get_fullmove_count(self, string):
        try:
            return int(string)
        except ValueError:
            raise InvalidFullmoveString

    def serialize(self, game_state: GameState):
        result = "{} {} {} {} {} {}"

        encoded_board = self._encode_board(game_state.board)
        encoded_to_move = self._encode_color_to_move(game_state.color_to_move)

        encoded_castling_perms = str(game_state.castling_permissions)

        en_passant = game_state.en_passant_target_square
        encoded_en_passant = self._encode_en_passant_target_square(en_passant)

        halfmove_clock = game_state.halfmove_clock
        encoded_halfmove_clock = self._encode_optional_int(halfmove_clock)

        fullmove_count = game_state.fullmove_count
        encoded_fullmove_count = self._encode_optional_int(fullmove_count)

        formatted_result = result.format(encoded_board, encoded_to_move,
                                         encoded_castling_perms,
                                         encoded_en_passant,
                                         encoded_halfmove_clock,
                                         encoded_fullmove_count)

        return formatted_result

    def _encode_board(self, board):
        matrix = board.matrix[::-1]

        encoded_ranks = []
        for rank in matrix:
            encoded_ranks.append(self._encode_board_rank(rank))

        return "/".join(encoded_ranks)

    def _encode_board_rank(self, rank):
        result = ""
        skip_tile_count = 0

        for piece in rank:
            if piece is None:
                skip_tile_count += 1
                continue

            piece_char = self._get_character_by_piece(piece)

            if skip_tile_count != 0:
                result += str(skip_tile_count)

            skip_tile_count = 0
            result += piece_char

        if result == "":
            return "8"

        if skip_tile_count != 0:
            result += str(skip_tile_count)

        return result

    def _get_character_by_piece(self, piece):
        result = ""

        if piece.piece_type is PieceType.KING:
            result = "k"
        elif piece.piece_type is PieceType.QUEEN:
            result = "q"
        elif piece.piece_type is PieceType.KNIGHT:
            result = "n"
        elif piece.piece_type is PieceType.ROOK:
            result = "r"
        elif piece.piece_type is PieceType.PAWN:
            result = "p"
        elif piece.piece_type is PieceType.BISHOP:
            result = "b"

        if piece.color is Color.WHITE:
            return result.upper()

        return result

    def _encode_color_to_move(self, color_to_move):
        if color_to_move is Color.WHITE:
            return "w"
        elif color_to_move is Color.BLACK:
            return "b"

    def _encode_castling_perms(self, castling_perms):
        result = ""

        if castling_perms.can_castle_kingside(Color.WHITE):
            result += "K"
        if castling_perms.can_castle_queenside(Color.BLACK):
            result += "Q"
        if castling_perms.can_castle_kingside(Color.BLACK):
            result += "k"
        if castling_perms.can_castle_queenside(Color.BLACK):
            result += "q"

        if result == "":
            return "-"

        return result

    def _encode_en_passant_target_square(self, en_passant_target):
        if en_passant_target is None:
            return "-"

        return str(en_passant_target)

    def _encode_optional_int(self, integer):
        if integer is None:
            return "-"

        return str(integer)
