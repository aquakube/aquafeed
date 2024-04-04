import pytest
from unittest.mock import Mock

from clients.plc import read


@pytest.fixture
def mock_requests_get_success(monkeypatch):
    # Create a mock version of the requests.get function
    mock_get = Mock()

    # Set up the mock to return a successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(return_value={'value': 1})
    mock_get.return_value = mock_response

    # Patch the requests.get function with the mock
    monkeypatch.setattr('requests.get', mock_get)


@pytest.fixture
def mock_requests_get_failure(monkeypatch):
    # Create a mock version of the requests.get function
    mock_get = Mock()

    # Set up the mock to return a successful response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status = Mock(side_effect=Exception('Test exception'))
    #ock_response.content = b'Test value'
    mock_get.return_value = mock_response

    # Patch the requests.get function with the mock
    monkeypatch.setattr('requests.get', mock_get)


def test_read_success(mock_requests_get_success):
    # Call the function under test, passing in the mock get function
    result = read('test_panel', 'test_property')

    # Check the result
    assert result == 1


def test_read_failure(mock_requests_get_failure):
    # Call the function under test, passing in the mock get function
    with pytest.raises(Exception):
        read('test_panel', 'test_property')
