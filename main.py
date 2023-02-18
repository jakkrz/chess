import files


def main():
    game_state = files.load_default_game()

    print(game_state.board)

    files.save_game_to_file("saved_games/game.fen", game_state)



if __name__ == "__main__":
    main()
