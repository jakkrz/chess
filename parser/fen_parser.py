from game_state.castling_permissions import CastlingPermissions
from game_state.game_state import GameState
from game_state.board import Board
from coordinate import Coordinate
import notation


class FenParser:
    def parse(self, string: str):
        result = GameState()
        fields = self._split_into_fields(string)

        result.board = self._parse_board(fields[0])
        result.color_to_move = notation.get_color_by_char(fields[1])
        result.castling_permissions = CastlingPermissions.from_string(fields[2])

        en_passant_target = self._parse_en_passant_target_square(fields[3])
        result.en_passant_target_square = en_passant_target

        result.halfmove_clock = int(fields[4])
        result.fullmove_count = int(fields[5])

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


    def _parse_en_passant_target_square(self, string):
        if string == "-":
            return None

        return Coordinate.from_string(string)


    def serialize(self, game_state: GameState):
        result = "{} {} {} {} {} {}"

        serialized_board = self._serialize_board(game_state.board)
        serialized_to_move = notation.get_char_by_color(game_state.color_to_move)

        en_passant = game_state.en_passant_target_square
        serialized_en_passant = self._serialize_en_passant_target_square(en_passant)

        formatted_result = result.format(serialized_board,
                                         serialized_to_move,
                                         game_state.castling_permissions,
                                         serialized_en_passant,
                                         game_state.halfmove_clock,
                                         game_state.fullmove_count)

        return formatted_result

    def _serialize_board(self, board):
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

            piece_char = notation.get_character_by_piece(piece)

            if skip_tile_count != 0:
                result += str(skip_tile_count)

            skip_tile_count = 0
            result += piece_char

        if result == "":
            return "8"

        if skip_tile_count != 0:
            result += str(skip_tile_count)

        return result

    def _serialize_en_passant_target_square(self, en_passant_target) -> str:
        if en_passant_target is None:
            return "-"

        return str(en_passant_target)

