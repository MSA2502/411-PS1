import pytest
import requests

from meal_max.utils.random_utils import get_random


RANDOM_NUMBER = 42
NUM_MEALS = 100

@pytest.fixture
def mock_random_org(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random()

    # Assert that the result is the mocked random number
    assert result == RANDOM_NUMBER, f"Expected random number {RANDOM_NUMBER}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with("https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new", timeout=5)
