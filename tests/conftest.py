import pytest
from files import load_default_game


@pytest.fixture
def default_game_state():
    return load_default_game()
