from game_state.game_state import GameState
from files import load_game_from_file, load_default_game
from user_input.enumeration_input import get_enumeration_input
from user_input.numerical_input import get_positive_number_input
from color import Color
from typing import Tuple
import socket
import re
from networking.connection import Connection


def get_game_state_input(prompt: str) -> GameState:
    while True:
        input_str = input(prompt)

        if input_str == "":
            return load_default_game()

        try:
            return load_game_from_file(input_str)
        except OSError:
            print(f"Could not read '{input_str}'. Try again")


def input_sequence() -> Tuple[GameState, Color, Connection]:
    choice = get_enumeration_input("Create or join game: ", ["create", "join"])

    if choice == "create":
        return create_game()
    else:
        return join_game()

    
def create_game() -> Tuple[GameState, Color, Connection]:
    debug = get_enumeration_input("What mode would you like to run the program?", ["debug", "normal"]) is "debug"
    game_state = get_game_state_input("Load game from file (empty=default game): ")
    client_color_string = get_enumeration_input("Enter color to play as: ", ["white", "black"])
    client_color = Color.WHITE if client_color_string == "white" else Color.BLACK
    connection = establish_network_connection_as_server(debug=debug)

    send_starting_data_through_connection(connection, client_color.opposite(), game_state)

    return game_state, client_color, connection


def send_starting_data_through_connection(conn: Connection, opponent_color: Color, game_state: GameState) -> None:
    conn.send_color(opponent_color)
    conn.send_game_state(game_state)


def receive_starting_data_from_connection(conn: Connection) -> Tuple[Color, GameState]:
    color = conn.receive_color()
    game_state = conn.receive_game_state()

    return color, game_state


def establish_network_connection_as_server(debug: bool) -> Connection:
    port = get_positive_number_input("Enter port to host connection on: ")

    print(f"IP address: {socket.gethostbyname(socket.gethostname())}")
    print("Waiting for enemy to connect...")
    conn = Connection.host_connection_on_port(port, debug=debug)

    return conn


def join_game() -> Tuple[GameState, Color, Connection]:
    conn = establish_network_connection_as_client()

    client_color, game_state = receive_starting_data_from_connection(conn)

    return game_state, client_color, conn


def establish_network_connection_as_client() -> Connection:
    while True:
        ip = get_ip_input("Enter the IP address to connect to: ")
        port = get_positive_number_input("Enter the port to connect to: ")
        

        try:
            conn = Connection.join_connection_at_address((ip, port))
        except TimeoutError:
            print(f"Could not establish connection at {ip}:{port}. Try again")
            continue

        return conn


def get_ip_input(prompt: str) -> str:
    while True:
        input_string = input(prompt)

        if is_ip_address(input_string):
            return input_string
        else:
            print(f"'{input_string}' is not a valid IP. Try again")

IP_ADDRESS_REGEX = r"(\d{1,3})(\.\d{1,3}){3}"

def is_ip_address(string: str) -> bool:
    return re.fullmatch(IP_ADDRESS_REGEX, string) is not None

