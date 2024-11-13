import pytest
from contextlib import contextmanager
import re
import sqlite3

from meal_max.models.kitchen_model import Meal
from dataclasses import dataclass
import logging
import os
import sqlite3

from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random
from meal_max.utils.sql_utils import get_db_connection
from meal_max.models.battle_model import BattleModel

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)


@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None


    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_cursor  # Return the mock cursor so we can set expectations per test


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""

    # Call the function to create a new meal
    create_meal(meal="Spaghetti", cuisine="Italian", price= 12.5, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Spaghetti", "Italian", 12.5, "MED")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate meal, cuisine, and price (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal, meals.cusiine, meals.price, meals.difficulty")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' already exists"):
        create_meal(meal="Spaghetti", cuisine="Italian", price=12.5, difficulty="MED")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal leaderboard (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_meals function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    mock_cursor.executescript.assert_called_once()

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal", "Cuisine", 12.5, "MED", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal", "Cuisine", 12.5, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999) 

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (artist = "Artist Name", title = "Song Title", year = 2022)
    mock_cursor.fetchone.return_value = (1, "Meal", "Cuisine", 12, "MED", False)

    # Call the function and check the result
    result = get_meal_by_name("Meal")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal", "Cuisine", 12, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard of meals with correct win percentages."""

    # Mocking database return values
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 20, "MED", 10, 5, 0.5),  # win_pct as 0.5 (50% after conversion)
        (2, "Meal B", "Cuisine B", 11, "HARD", 20, 5, 0.25),  # win_pct as 0.25 (25% after conversion)
        (3, "Meal C", "Cuisine C", 30, "LOW", 5, 5, 1.0)  # win_pct as 1.0 (100% after conversion)
    ]

    # Call the get_leaderboard function
    meals = get_leaderboard()

    # Updated expected result to match the correct win_pct calculations
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 20, "difficulty": "MED", "battles": 10, "wins": 5, "win_pct": 50.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 11, "difficulty": "HARD", "battles": 20, "wins": 5, "win_pct": 25.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 30, "difficulty": "LOW", "battles": 5, "wins": 5, "win_pct": 100.0}
    ]

    # Assert the results match the expected output
    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Check the SQL query structure
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC ")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_ordered_by_wins(mock_cursor):
    """Test retrieving all meals ordered by wins."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (2, "Meal B", "Cuisine B", 11, "HARD", 20, 5, 0.25),  # win_pct as 0.25 (25% after conversion)
        (1, "Meal A", "Cuisine A", 20, "MED", 10, 5, 0.5),  # win_pct as 0.5 (50% after conversion)
        (3, "Meal C", "Cuisine C", 30, "LOW", 5, 5, 1.0)  # win_pct as 1.0 (100% after conversion)
    ]

    # Call the get_leaderboard function with sort_by = wins
    meals = get_leaderboard(sort_by="wins")

    # Ensure the results are sorted by wins
    expected_result = [
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 11, "difficulty": "HARD", "battles": 20, "wins": 5, "win_pct": 25.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 20, "difficulty": "MED", "battles": 10, "wins": 5, "win_pct": 50.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 30, "difficulty": "LOW", "battles": 5, "wins": 5, "win_pct": 100.0}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."



def test_update_meal_stats(mock_cursor):
    """Test updating the stats of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    update_meal_stats(meal_id, result="win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, result="deleted")

    # Ensure that no SQL query for updating stats was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1, ))
