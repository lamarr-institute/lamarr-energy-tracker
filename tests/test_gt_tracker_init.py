import pytest
from unittest.mock import patch, mock_open
from datetime import datetime

from lamarr_energy_tracker.ground_truth_tracking import GroundTruthTracker


@patch.dict("os.environ", {"LET_GT_HOST": "localhost", "LET_GT_PORT": "8000"})
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_tracker_init_env(mock_available, mock_hostname):

    mock_available.return_value = True

    tracker = GroundTruthTracker()

    assert tracker.server_host == "localhost"
    assert tracker.server_port == "8000"


@patch.dict("os.environ", {"LET_GT_HOST": "localhost", "LET_GT_PORT": "8000"})
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_tracker_init_non_available_no_crash(mock_available, mock_hostname):
    """Test that tracker initializes with warning when crash_if_unavailable=False"""
    mock_available.side_effect = Exception("Server not available")
    
    tracker = GroundTruthTracker(crash_if_unavailable=False)
    
    assert tracker.server_host is None
    assert tracker.server_port is None
    assert tracker.crash_if_unavailable is False
    
    # Test start() returns dummy values
    start_result = tracker.start()
    expected_start = {
        'energy_consumed': -1,
        'start_time': None,
        'timestamp': None,
        'duration': -1,
        'tracking_mode': 'GroundTruth'
    }
    assert start_result == expected_start
    
    # Test stop() returns dummy values with tracking_mode
    stop_result = tracker.stop()
    expected_stop = {'energy_consumed': -1, 'start_time': None, 'timestamp': None, 'duration': -1, 'tracking_mode': 'GroundTruth'}
    assert stop_result == expected_stop


@patch.dict("os.environ", {"LET_GT_HOST": "localhost", "LET_GT_PORT": "8000"})
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.send_command")
def test_tracker_start_stop_uses_server_when_available(mock_send_command, mock_available, mock_hostname):
    """Regression test: crash_if_unavailable=False should not use dummy results when server is reachable."""
    mock_available.return_value = True

    mock_send_command.side_effect = [
        {
            'energy_consumed': 1.23,
            'start_time': datetime(2024, 1, 1, 0, 0, 0),
            'timestamp': datetime(2024, 1, 1, 0, 1, 0),
            'duration': 60
        },
        {
            'energy_consumed': 2.34,
            'start_time': datetime(2024, 1, 1, 0, 0, 0),
            'timestamp': datetime(2024, 1, 1, 0, 2, 0),
            'duration': 120
        }
    ]

    tracker = GroundTruthTracker(crash_if_unavailable=False)

    start_result = tracker.start()
    stop_result = tracker.stop()

    assert start_result['energy_consumed'] == 1.23
    assert stop_result['energy_consumed'] == 2.34
    assert stop_result['tracking_mode'] == 'GroundTruth'
    assert mock_send_command.call_count == 2
    mock_send_command.assert_any_call("localhost", "start", "8000")
    mock_send_command.assert_any_call("localhost", "stop", "8000")


@patch.dict("os.environ", {}, clear=True)
@patch("builtins.open", new_callable=mock_open, read_data="localhost:8000")
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_tracker_init_remote_config(mock_available, mock_hostname, mock_file):

    mock_available.return_value = True

    tracker = GroundTruthTracker()

    assert tracker.server_host == "localhost"