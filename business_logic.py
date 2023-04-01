from engine.engine import (
    verify_move,
    do_move,
    is_in_checkmate,
)
from move import Move
from move import (
    Move,
)
from environment import Environment
from networking.connection import Connection


def verify_and_do_move(environment: Environment, move: Move):
    with environment.game_state_lock:
        if not verify_move(environment.game_state, move):
            raise ValueError("illegal move")

        do_move(environment.game_state, move)


def play_client_move(environment: Environment, connection: Connection):
    move = environment.move_queue.get()
    connection.send_move(move)

    verify_and_do_move(environment, move)


def play_opponent_move(environment: Environment, connection: Connection):
    move = connection.receive_move()

    verify_and_do_move(environment, move)


def business_logic(environment: Environment, connection: Connection):
    while True:
        if is_in_checkmate(environment.game_state):
            raise ValueError("checkmate")

        if environment.game_state.color_to_move is environment.client_color:
            play_client_move(environment, connection)
        else:
            play_opponent_move(environment, connection)
