from abc import ABC


class Parser(ABC):

    def parse(self, string):
        pass

    def serialize(self, game_state):
        pass
