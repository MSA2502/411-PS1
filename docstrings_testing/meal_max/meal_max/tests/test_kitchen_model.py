import pytest
from contextlib import contextmanager
import re
import sqlite3

from meal_max.models.kitchen_model import Meal
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


@pytest.fixture()
def mock_db_connection(mocker):
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

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""

    # Call the function to create a new song
    create_meal(meal="Meal", cuisine="Cuisine", price="price", float="Float")

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

def Meal():
    """Fixture to provide a new instance of Meal for each test."""
    return Meal()

