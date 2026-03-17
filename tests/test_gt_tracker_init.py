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


@patch.dict("os.environ", {}, clear=True)
@patch("builtins.open", new_callable=mock_open, read_data="localhost:8000")
@patch("socket.gethostname", return_value="host1")
@patch("lamarr_energy_tracker.ground_truth_tracking.GroundTruthTracker.is_available")
def test_tracker_init_remote_config(mock_available, mock_hostname, mock_file):

    mock_available.return_value = True

    tracker = GroundTruthTracker()

    assert tracker.server_host == "localhost"