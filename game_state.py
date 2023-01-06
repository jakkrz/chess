from dataclasses import dataclass
from copy import deepcopy
from loader import load_board_from_file
from enum import Enum
from piece import Piece, PieceType
from move import Move


class MotionsAttacks:
    motions: set[tuple[int, int]]
    attacks: set[tuple[int, int]]

    def __init__(self):
        self.motions = set()
        self.attacks = set()


@dataclass
class GameState:
    """
    State stores the state of the chess game. For more info, check out: https://en.wikipedia.org/wiki/Board_representation_(computer_chess)#Board_state
    For simplicites sake, the 50 move rule has been ommitted.
    """

    board: list[list[Piece | None]]
    am_white: bool
    my_turn: bool
    white_can_castle_kingside: bool
    white_can_castle_queenside: bool
    black_can_castle_kingside: bool
    black_can_castle_queenside: bool
    pawn_double_move: tuple[int, int] | None

    def __init__(self, am_white: bool):
        self.board = load_board_from_file("standard_layout.txt")
        self.am_white = am_white
        self.my_turn = am_white
        self.white_can_castle_kingside = True
        self.white_can_castle_queenside = True
        self.black_can_castle_kingside = True
        self.black_can_castle_queenside = True
        self.pawn_double_move = None

    def get_possible_moves_in_direction(
        self, x: int, y: int, direction_x: int, direction_y: int
    ) -> MotionsAttacks:
        result = MotionsAttacks()
        piece = self.board[y][x]
        am_white = piece.is_white

        x += direction_x
        y += direction_y

        while 0 <= x <= 7 and 0 <= y <= 7:
            if self.board[y][x] is None:
                result.motions.add((x, y))
                x += direction_x
                y += direction_y
                continue

            other_piece = self.board[y][x]

            if other_piece.is_white != am_white:
                result.attacks.add((x, y))

            break

        return result

    def union_of_sets(self, *args):
        result = set()

        for s in args:
            result.update(s)

        return result

    def get_possible_moves_castle(self, x: int, y: int):
        ma1 = self.get_possible_moves_in_direction(x, y, 1, 0)
        ma2 = self.get_possible_moves_in_direction(x, y, 0, 1)
        ma3 = self.get_possible_moves_in_direction(x, y, -1, 0)
        ma4 = self.get_possible_moves_in_direction(x, y, 0, -1)

        result = MotionsAttacks()
        result.motions = self.union_of_sets(
            ma1.motions, ma2.motions, ma3.motions, ma4.motions
        )
        result.attacks = self.union_of_sets(
            ma1.attacks, ma2.attacks, ma3.attacks, ma4.attacks
        )

        return result

    def get_possible_moves_bishop(self, x: int, y: int):
        ma1 = self.get_possible_moves_in_direction(x, y, 1, 1)
        ma2 = self.get_possible_moves_in_direction(x, y, -1, 1)
        ma3 = self.get_possible_moves_in_direction(x, y, 1, -1)
        ma4 = self.get_possible_moves_in_direction(x, y, -1, -1)

        result = MotionsAttacks()
        result.motions = self.union_of_sets(
            ma1.motions, ma2.motions, ma3.motions, ma4.motions
        )
        result.attacks = self.union_of_sets(
            ma1.attacks, ma2.attacks, ma3.attacks, ma4.attacks
        )

        return result

    def get_possible_moves_queen(self, x: int, y: int):
        ma1 = self.get_possible_moves_castle(x, y)
        ma2 = self.get_possible_moves_bishop(x, y)

        result = MotionsAttacks()
        result.motions = self.union_of_sets(ma1.motions, ma2.motions)
        result.attacks = self.union_of_sets(ma1.attacks, ma2.attacks)

        return result

    def update_motions_attacks_for_position(
        self, x: int, y: int, ma: MotionsAttacks, am_white: bool
    ):
        if y > 7 or y < 0 or x > 7 or x < 0:
            return

        if self.board[y][x] is None:
            ma.motions.add((x, y))

        piece = self.board[y][x]

        if piece is not None and piece.is_white != am_white:
            ma.attacks.add((x, y))

    def get_possible_moves_king(self, x: int, y: int):
        am_white = self.board[y][x].is_white
        result = MotionsAttacks()

        self.update_motions_attacks_for_position(x + 1, y, result, am_white)
        self.update_motions_attacks_for_position(x + 1, y + 1, result, am_white)
        self.update_motions_attacks_for_position(x + 1, y - 1, result, am_white)
        self.update_motions_attacks_for_position(x, y + 1, result, am_white)
        self.update_motions_attacks_for_position(x, y - 1, result, am_white)
        self.update_motions_attacks_for_position(x - 1, y, result, am_white)
        self.update_motions_attacks_for_position(x - 1, y + 1, result, am_white)
        self.update_motions_attacks_for_position(x - 1, y - 1, result, am_white)

        enemy_king_pos = self.get_king_position(not am_white)
        enemy_king_x, enemy_king_y = enemy_king_pos

        enemy_king_surroundings = set(
            [
                (enemy_king_x + 1, enemy_king_y + 1),
                (enemy_king_x + 1, enemy_king_y),
                (enemy_king_x + 1, enemy_king_y - 1),
                (enemy_king_x, enemy_king_y + 1),
                (enemy_king_x, enemy_king_y - 1),
                (enemy_king_x - 1, enemy_king_y + 1),
                (enemy_king_x - 1, enemy_king_y),
                (enemy_king_x - 1, enemy_king_y - 1),
            ]
        )

        result.motions -= enemy_king_surroundings
        result.attacks -= enemy_king_surroundings

        if self.is_in_check(am_white):
            return result

        if am_white:
            if self.white_can_castle_kingside:
                if self.board[7][5] is None and self.board[7][6] is None:
                    result.motions.add((6, 7))

            if self.white_can_castle_queenside:
                if (
                    self.board[7][1] is None
                    and self.board[7][2] is None
                    and self.board[7][3] is None
                ):
                    result.motions.add((2, 7))
        else:
            if self.black_can_castle_kingside:
                if self.board[0][5] is None and self.board[0][6] is None:
                    result.motions.add((6, 0))
            if self.black_can_castle_queenside:
                if (
                    self.board[0][1] is None
                    and self.board[0][2] is None
                    and self.board[0][3] is None
                ):
                    result.motions.add((2, 0))

        result.motions -= enemy_king_surroundings
        result.attacks -= enemy_king_surroundings
        return result

    def get_possible_moves_horse(self, x: int, y: int):
        am_white = self.board[y][x].is_white
        result = MotionsAttacks()

        self.update_motions_attacks_for_position(x + 2, y + 1, result, am_white)
        self.update_motions_attacks_for_position(x - 2, y + 1, result, am_white)
        self.update_motions_attacks_for_position(x + 2, y - 1, result, am_white)
        self.update_motions_attacks_for_position(x - 2, y - 1, result, am_white)
        self.update_motions_attacks_for_position(x + 1, y + 2, result, am_white)
        self.update_motions_attacks_for_position(x - 1, y + 2, result, am_white)
        self.update_motions_attacks_for_position(x + 1, y - 2, result, am_white)
        self.update_motions_attacks_for_position(x - 1, y - 2, result, am_white)

        return result

    def update_attack_only(self, x: int, y: int, ma: MotionsAttacks, am_white):
        if x < 0 or x > 7 or y < 0 or y > 7:
            return

        if self.board[y][x] is None:
            return

        if self.board[y][x].is_white != am_white:
            ma.attacks.add((x, y))

    def get_possible_moves_pawn(self, x: int, y: int):
        am_white = self.board[y][x].is_white

        result = MotionsAttacks()

        forwards = -1 if am_white else 1
        second_row = 6 if am_white else 1
        fifth_row = 3 if am_white else 4
        sixth_row = 2 if am_white else 5

        self.update_attack_only(x + 1, y + forwards, result, am_white)
        self.update_attack_only(x - 1, y + forwards, result, am_white)

        if y not in [0, 7]:
            if self.board[y + forwards][x] is None:
                result.motions.add((x, y + forwards))

                if y == second_row and self.board[y + forwards * 2][x] is None:
                    result.motions.add((x, y + forwards * 2))

        if self.pawn_double_move in [x - 1, x + 1] and y == fifth_row:
            result.attacks.add((self.pawn_double_move, sixth_row))

        return result

    def get_possible_moves(
        self, x: int, y: int, shallow: bool = False
    ) -> MotionsAttacks:
        piece = self.board[y][x]

        match piece.piece_type:
            case PieceType.BISHOP:
                result = self.get_possible_moves_bishop(x, y)

            case PieceType.CASTLE:
                result = self.get_possible_moves_castle(x, y)

            case PieceType.QUEEN:
                result = self.get_possible_moves_queen(x, y)

            case PieceType.KING:
                result = self.get_possible_moves_king(x, y)

            case PieceType.HORSE:
                result = self.get_possible_moves_horse(x, y)

            case PieceType.PAWN:
                result = self.get_possible_moves_pawn(x, y)

        if not shallow:
            motions_to_remove = set()
            for motion in result.motions:
                corresponding_move = Move((x, y), motion)

                if not self.does_move_evade_check(corresponding_move, piece.is_white):
                    motions_to_remove.add(motion)
            result.motions -= motions_to_remove

            attacks_to_remove = set()
            for attack in result.attacks:
                corresponding_move = Move((x, y), attack)

                if not self.does_move_evade_check(corresponding_move, piece.is_white):
                    attacks_to_remove.add(attack)
            result.attacks -= attacks_to_remove

        return result

    def get_king_position(self, white: bool):
        for y, piece_row in enumerate(self.board):
            for x, piece in enumerate(piece_row):
                if piece is None:
                    continue

                if piece.piece_type == PieceType.KING and piece.is_white == white:
                    return x, y

    def is_in_check(self, white: bool):
        king_pos = self.get_king_position(white)

        for y, piece_row in enumerate(self.board):
            for x, piece in enumerate(piece_row):
                if (
                    piece is not None
                    and piece.is_white != white
                    and piece.piece_type != PieceType.KING
                ):
                    if king_pos in self.get_possible_moves(x, y, True).attacks:
                        return True

        return False

    def copy(self):
        new_game_state = GameState(self.am_white)

        new_game_state.board = deepcopy(self.board)
        new_game_state.my_turn = self.my_turn
        new_game_state.white_can_castle_kingside = self.white_can_castle_kingside
        new_game_state.white_can_castle_queenside = self.white_can_castle_queenside
        new_game_state.black_can_castle_kingside = self.black_can_castle_kingside
        new_game_state.black_can_castle_queenside = self.black_can_castle_queenside
        new_game_state.pawn_double_move = self.pawn_double_move

        return new_game_state

    def adopt_copy(self, copy):
        self.am_white = copy.am_white
        self.my_turn = copy.my_turn
        self.pawn_double_move = copy.pawn_double_move
        self.white_can_castle_kingside = copy.white_can_castle_kingside
        self.white_can_castle_queenside = copy.white_can_castle_queenside
        self.black_can_castle_kingside = copy.black_can_castle_kingside
        self.black_can_castle_queenside = copy.black_can_castle_queenside
        self.board = copy.board

    def verify_move(self, move: Move, my_move) -> bool:
        source_x, source_y = move.source
        dest = move.destination
        dest_x, dest_y = dest

        if self.my_turn != my_move:
            return False

        if self.board[source_y][source_x] is None:
            return False

        if (self.board[source_y][source_x].is_white == self.am_white) != my_move:
            return False

        is_white = self.am_white == my_move

        ma = self.get_possible_moves(source_x, source_y)
        possible_motions = ma.motions
        possible_attacks = ma.attacks

        if dest not in possible_motions and dest not in possible_attacks:
            return False

        if not self.does_move_evade_check(move, is_white):
            return False

        return True

    def does_move_evade_check(self, move: Move, white_in_check: bool):
        stored_state = self.copy()
        self.make_move(move)

        if self.is_in_check(white_in_check):
            self.adopt_copy(stored_state)
            return False

        self.adopt_copy(stored_state)
        return True

    def make_move(self, move: Move):
        source_x, source_y = move.source
        dest_x, dest_y = move.destination

        piece_being_moved = self.board[source_y][source_x]

        if piece_being_moved.piece_type == PieceType.KING:
            if dest_x - source_x == 2:
                self.board[source_y][5] = self.board[source_y][7]
                self.board[source_y][7] = None
            elif source_x - dest_x == 2:
                self.board[source_y][3] = self.board[source_y][0]
                self.board[source_y][0] = None

            if piece_being_moved.is_white:
                self.white_can_castle_kingside = False
                self.white_can_castle_queenside = False
            else:
                self.black_can_castle_kingside = False
                self.black_can_castle_queenside = False

        if piece_being_moved.piece_type == PieceType.CASTLE:
            if piece_being_moved.is_white:
                if source_x == 0 and source_y == 7:
                    self.white_can_castle_queenside = False
                elif source_x == 7 and source_y == 7:
                    self.white_can_castle_kingside = False
            else:
                if source_x == 0 and source_y == 0:
                    self.black_can_castle_queenside = False
                elif source_x == 7 and source_y == 0:
                    self.black_can_castle_kingside = False

        fifth_row = 3 if piece_being_moved.is_white else 4

        if piece_being_moved.piece_type == PieceType.PAWN:
            if dest_x == self.pawn_double_move and source_y == fifth_row:
                self.board[fifth_row][dest_x] = None

            if abs(dest_y - source_y) == 2:
                self.pawn_double_move = source_x
            else:
                self.pawn_double_move = None
        else:
            self.pawn_double_move = None

        piece_being_attacked = self.board[dest_y][dest_x]

        if piece_being_attacked is not None:
            if piece_being_attacked.piece_type == PieceType.CASTLE:
                if piece_being_attacked.is_white:
                    if dest_x == 0 and dest_y == 7:
                        self.white_can_castle_queenside = False
                    elif dest_x == 7 and dest_y == 7:
                        self.white_can_castle_kingside = False
                else:
                    if dest_x == 0 and dest_y == 0:
                        self.black_can_castle_queenside = False
                    elif dest_x == 7 and dest_y == 0:
                        self.black_can_castle_kingside = False

        self.board[dest_y][dest_x] = self.board[source_y][source_x]
        self.board[source_y][source_x] = None

        self.my_turn = not self.my_turn

    def possible_moves_exist(self, white: bool):
        for y, piece_row in enumerate(self.board):
            for x, piece in enumerate(piece_row):
                if self.board[y][x] is None:
                    continue

                if self.board[y][x].is_white != white:
                    continue

                possible_moves = self.get_possible_moves(x, y)

                if possible_moves.motions == set() and possible_moves.attacks == set():
                    continue

                return True

        return False

    def is_in_checkmate(self, white: bool):
        return self.is_in_check(white) and not self.possible_moves_exist(white)

    def promote_pawn(self, piece_type, am_white):
        last_row = 0 if am_white else 7

        change_index = None
        for x, piece in enumerate(self.board[last_row]):
            if piece is not None and piece.piece_type == PieceType.PAWN:
                change_index = x
                break

        if change_index is not None:
            self.board[last_row][change_index].piece_type = piece_type
