from user_input.user_input import input_sequence
from queue import Queue
import threading
import pygame
from rendering.rendering import render_logic
from environment import Environment
from business_logic import business_logic

pygame.init()


if __name__ == "__main__":
    game_state, client_color, connection = input_sequence()

    shared_environment = Environment(
        game_state      = game_state,
        game_state_lock = threading.Lock(),
        move_queue      = Queue(maxsize=1),
        close_event     = threading.Event(),
        client_color    = client_color
    )

    business_logic_thread = threading.Thread(target=business_logic, args=(shared_environment, connection))

    business_logic_thread.start()

    render_logic(shared_environment)
