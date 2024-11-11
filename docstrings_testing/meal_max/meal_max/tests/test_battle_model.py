import pytest

from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel

@pytest.fixture()
def battel_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("music_collection.models.playlist_model.update_play_count")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Italian', 10, 'MED')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Chinese', 15, 'LOW')

@pytest.fixture
def sample_battle_model(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Add Meal Management Test Cases
##################################################

def test_add_meal_to_battle(battle_model, sample_meal1):
    """Test adding a meal to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_add_two_meals_to_battle(battle_model, sample_meal2):
    """Test adding a second meal to the battle."""
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[1].meal == 'Meal 2'

def test_add_third_meal_to_battle(battle_model, sample_meal2):
    """Test adding a second meal to the battle."""
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal2)