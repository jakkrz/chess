from abc import ABC
from game_state.game_state import GameState


class Parser(ABC):
    def parse(self, string: str):
        pass

    def serialize(self, game_state: GameState):
        pass
