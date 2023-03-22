from user_input.user_input import input_sequence
from parser.fen_parser import FenParser


def main():
    fen_parser = FenParser()
    game_state, color, conn = input_sequence()
    print(fen_parser.serialize(game_state), color)


if __name__ == "__main__":
    main()
