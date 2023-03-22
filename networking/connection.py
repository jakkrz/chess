import socket
from move import Move
from typing import Tuple
from game_state.game_state import GameState
from color import Color
from networking.serialization import (
    serialize_move,
    deserialize_move,
    serialize_game_state,
    deserialize_game_state,
    serialize_color,
    deserialize_color
)

Address = Tuple[str, int]
PAYLOAD_SPECIFIER_LENGTH = 32

class Connection:
    @staticmethod
    def host_connection_on_port(port: int, debug=False) -> "Connection":
        host_socket = socket.socket()
        ip = "" if debug else socket.gethostname()

        host_socket.bind((ip, port))
        host_socket.listen(1)

        partner_socket, partner_address = host_socket.accept()

        return Connection(partner_socket, partner_address)

    @staticmethod
    def join_connection_at_address(addr: Address) -> "Connection":
        client_socket = socket.socket()
        client_socket.connect(addr)

        return Connection(client_socket, addr)

    def get_partner_address(self) -> Address:
        return self.partner_address

    def __init__(self, _socket: socket.socket, partner_address: Address):
        self.socket = _socket
        self.partner_address = partner_address

    def receive_move(self) -> Move:
        move_bytes = self._receive_bytes()
        deserialized_move = deserialize_move(move_bytes)

        return deserialized_move

    def send_move(self, move: Move) -> None:
        serialized_move = serialize_move(move)

        self._send_bytes(serialized_move)

    def send_game_state(self, game_state: GameState) -> None:
        serialized_game_state = serialize_game_state(game_state)

        self._send_bytes(serialized_game_state)

    def receive_game_state(self) -> GameState:
        game_state_bytes = self._receive_bytes()
        deserialized_game_state = deserialize_game_state(game_state_bytes)

        return deserialized_game_state
    
    def send_color(self, color: Color) -> None:
        serialized_color = serialize_color(color)
        
        self._send_bytes(serialized_color)

    def receive_color(self) -> Color:
        color_bytes = self._receive_bytes()
        color = deserialize_color(color_bytes)

        return color

    def _send_bytes(self, bytes_to_send: bytes) -> None:
        payload_length = len(bytes_to_send)

        self._send_payload_length(payload_length)
        self.socket.send(bytes_to_send)

    def _send_payload_length(self, payload_length: int) -> None:
        self.socket.send(payload_length.to_bytes(PAYLOAD_SPECIFIER_LENGTH, "big", signed=False))

    def _receive_bytes(self) -> bytes:
        payload_length = self._receive_payload_length()

        return self.socket.recv(payload_length)

    def _receive_payload_length(self) -> int:
        bytes_received = self.socket.recv(PAYLOAD_SPECIFIER_LENGTH)

        return int.from_bytes(bytes_received, "big", signed=False)

    def terminate(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
