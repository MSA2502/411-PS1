import pytest

from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.get_random", return_value=2)

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

def test_add_two_meals_to_battle(battle_model, sample_meal1, sample_meal2):
    """Test adding a second meal to the battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[1].meal == 'Meal 2'

def test_add_third_meal_to_battle(battle_model, sample_meal1, sample_meal2):
    """Test adding a third meal to the battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal2)

##################################################
# Clear Meals Management Test Cases
##################################################

def test_clear_battle(battle_model, sample_meal1):
    """Test clearing the entire battle."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants should be empty after clearing"

##################################################
# Get Combatants Test Cases
##################################################

def test_get_combatants(battle_model, sample_battle_model):
    """Test successfully retrieving all combatants from the battle."""
    battle_model.combatants.extend(sample_battle_model)

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

##################################################
# Get Battle Score Test Cases
##################################################

def test_get_battle_score_meal1(battle_model, sample_meal1):
    """Test successfully retrieving battle score for meal 1."""

    assert battle_model.get_battle_score(sample_meal1) == 68

def test_get_battle_score_meal2(battle_model, sample_meal2):
    """Test successfully retrieving battle score for meal 2."""

    assert battle_model.get_battle_score(sample_meal2) == 102

##################################################
# Battle Test Cases
##################################################

def test_battle(battle_model, sample_meal2, sample_battle_model, mock_update_meal_stats, mock_get_random):
    """Test battling."""
    battle_model.combatants.extend(sample_battle_model)

    # Assert that CURRENT_TRACK_NUMBER has been updated to 2
    assert battle_model.battle() == sample_meal2.meal

    # Assert that update_play_count was called with the id of the first song
    mock_update_meal_stats.assert_any_call(1, "loss")
    mock_update_meal_stats.assert_any_call(2, "win")

    mock_get_random.assert_called_once_with()
    assert len(battle_model.combatants) == 1, "Should remove loser"

def test_battle_not_enough_meals(battle_model, sample_meal1):
    """Test battling with 1 meal."""
    battle_model.prep_combatant(sample_meal1)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
