from parser.fen_parser import FenParser
import pathlib
from game_state.game_state import GameState


def read_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def write_to_file(filepath: str, string: str):
    with open(filepath, "w") as f:
        f.write(string)


_parser_mapping = {".fen": FenParser()}


def _get_file_extension(filepath):
    return pathlib.Path(filepath).suffix


def _get_parser_for_file(filepath):
    file_extension = _get_file_extension(filepath)

    return _parser_mapping[file_extension]


def load_game_from_file(filepath: str) -> GameState:
    parser = _get_parser_for_file(filepath)
    file_content = read_file(filepath)

    return parser.parse(file_content)


def save_game_to_file(filepath: str, game_state: GameState):
    parser = _get_parser_for_file(filepath)

    write_to_file(filepath, parser.serialize(game_state))


def load_default_game() -> GameState:
    return load_game_from_file("layout.fen")
