import pytest

from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel


@pytest.fixture()
def Meal():
    """Fixture to provide a new instance of Meal for each test."""
    return Meal()

