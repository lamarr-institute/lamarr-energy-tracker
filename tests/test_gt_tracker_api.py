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


@patch.dict("os.environ", {"LET_GT_HOST": "localhost", "LET_GT_PORT": "8000"})
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.send_command")
def test_stop_return_format(mock_send_command, mock_available, mock_hostname):
    """Test if stop() returns properly formatted emissions data"""
    mock_available.return_value = True
    
    # Mock the send_command return value
    mock_send_command.return_value = {
        'energy_consumed': 0.123,
        'start_time': datetime(2024, 1, 1, 0, 0, 0),
        'timestamp': datetime(2024, 1, 1, 1, 0, 0),
        'duration': 3600.0
    }
    
    tracker = GroundTruthTracker()
    results = tracker.stop()
    
    assert isinstance(results, dict), "Stop should return a dictionary"
    # check energy data
    assert isinstance(results['energy_consumed'], float), "Energy should be a float"
    assert results['energy_consumed'] >= 0, "Energy should be non-negative"
    # check duration data
    assert isinstance(results['duration'], float), "Duration should be a float"
    assert results['duration'] >= 0, "Duration should be non-negative"
    # check timestamp data
    assert isinstance(results['timestamp'], datetime), "Timestamp should be a datetime object"
    # check start_time data
    assert isinstance(results['start_time'], datetime), "Start time should be a datetime object"
    # check tracking_mode
    assert results['tracking_mode'] == 'groundtruth', "Tracking mode should be 'groundtruth'"