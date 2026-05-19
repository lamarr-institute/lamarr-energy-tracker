import pytest
from unittest.mock import patch, mock_open

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
    """Test that tracker initializes with warning when non_available_crash=False"""
    mock_available.side_effect = Exception("Server not available")
    
    tracker = GroundTruthTracker(non_available_crash=False)
    
    assert tracker.server_host is None
    assert tracker.server_port is None
    assert tracker.non_available_crash is False
    
    # Test start() returns dummy values
    start_result = tracker.start()
    expected_start = {'energy_consumed': -1, 'start_time': None, 'timestamp': None, 'duration': -1}
    assert start_result == expected_start
    
    # Test stop() returns dummy values with tracking_mode
    stop_result = tracker.stop()
    expected_stop = {'energy_consumed': -1, 'start_time': None, 'timestamp': None, 'duration': -1, 'tracking_mode': 'GroundTruth'}
    assert stop_result == expected_stop


@patch.dict("os.environ", {}, clear=True)
@patch("builtins.open", new_callable=mock_open, read_data="localhost:8000")
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_tracker_init_remote_config(mock_available, mock_hostname, mock_file):

    mock_available.return_value = True

    tracker = GroundTruthTracker()

    assert tracker.server_host == "localhost"