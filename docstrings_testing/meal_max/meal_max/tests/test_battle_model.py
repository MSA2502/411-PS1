import pytest

from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel

@pytest.fixture()
def playlist_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("music_collection.models.playlist_model.update_play_count")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Artist 1', 'Song 1', 2022, 'Pop', 180)

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Artist 2', 'Song 2', 2021, 'Rock', 155)

@pytest.fixture
def sample_battle_model(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]