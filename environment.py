from dataclasses import dataclass
from game_state.game_state import GameState
from color import Color
from queue import Queue
import threading

@dataclass
class Environment:
    game_state: GameState
    game_state_lock: threading.Lock
    move_queue: Queue
    close_event: threading.Event
    client_color: Color
