import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from lamarr_energy_tracker.ground_truth_tracking import (
    GroundTruthTracker,
    GT_FMT
)


@patch("requests.get")
def test_all_available(mock_get):

    mock_response = Mock()
    mock_response.json.return_value = ["host1", "host2"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = GroundTruthTracker.all_available("localhost", 8000)

    assert "host1" in result


@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.all_available")
def test_is_available(mock_all_available, mock_hostname):

    mock_all_available.return_value = ["host1", "host2"]

    assert GroundTruthTracker.is_available("localhost", 8000)


@patch("socket.gethostname", return_value="host1")
@patch("requests.get")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_send_command_parses_datetime(mock_available, mock_get, mock_hostname):

    mock_available.return_value = True

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "start_time": "2024-01-01T00:00:00",
        "timestamp": "2024-01-01T01:00:00",
        "duration": 3600,
        "energy_consumed": 10
    }
    mock_get.return_value = mock_response

    result = GroundTruthTracker.send_command("localhost", "start", 8000)

    assert isinstance(result["start_time"], datetime)
    assert result["duration"] == 3600