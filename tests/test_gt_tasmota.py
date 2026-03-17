import pytest
from datetime import datetime
from unittest.mock import patch, Mock

from lamarr_energy_tracker.ground_truth_tracking import (
    send_tasmota_query,
    tasmota_start,
    tasmota_stop,
    GT_FMT
)


MOCK_STATUS_RESPONSE = {
    "StatusSNS": {
        "ENERGY": {
            "Total": 1.5,
            "TotalStartTime": "2024-01-01T00:00:00"
        },
        "Time": "2024-01-01T01:00:00"
    }
}


@patch("requests.get")
def test_send_tasmota_query_parses_response(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = MOCK_STATUS_RESPONSE
    mock_get.return_value = mock_response

    result = send_tasmota_query("1.2.3.4", "Status%208")

    assert result["energy_consumed"] == 1.5 * 3600
    assert result["duration"] == 3600
    assert result["start_time"] == "2024-01-01T00:00:00"


@patch("lamarr_energy_tracker.ground_truth_tracking.send_tasmota_query")
def test_tasmota_start_resets_and_returns(mock_query):

    mock_query.side_effect = [
        None,                          # EnergyRes
        {"timestamp": "2024-01-01T00:00:00",
         "start_time": "2024-01-01T00:00:00",
         "energy_consumed": 0,
         "duration": 0},
        None, None, None,              # reset commands
        {"timestamp": "2024-01-01T01:00:00",
         "start_time": "2024-01-01T00:00:00",
         "energy_consumed": 10,
         "duration": 3600},
    ]

    result = tasmota_start("1.2.3.4")

    assert result["timestamp"] == "2024-01-01T01:00:00"


@patch("lamarr_energy_tracker.ground_truth_tracking.send_tasmota_query")
def test_tasmota_stop(mock_query):
    mock_query.side_effect = [
        None,
        {"timestamp": "2024-01-01T01:00:00",
         "start_time": "2024-01-01T00:00:00",
         "energy_consumed": 10,
         "duration": 3600}
    ]

    result = tasmota_stop("1.2.3.4")
    assert result["duration"] == 3600