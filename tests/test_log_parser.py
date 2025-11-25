import pytest
import pandas as pd
from pandas import DataFrame
from app.log_parser import LogParser


@pytest.fixture
def sample_plugin_logs():
    """
    Creates a minimal valid log set for testing.
    Includes start, end, info, and error logs.
    """
    data = [
        {
            "Timestamp": "2025-11-24T05:00:00.000Z",
            "Level": "INFO",
            "Message": "[MyPlugin]: Started executing plug-in instance",
        },
        {
            "Timestamp": "2025-11-24T05:00:01.000Z",
            "Level": "INFO",
            "Message": "Starting user code execution",
        },
        {
            "Timestamp": "2025-11-24T05:00:03.000Z",
            "Level": "INFO",
            "Message": "Successfully executed user-defined function.",
        },
        {
            "Timestamp": "2025-11-24T05:00:04.000Z",
            "Level": "INFO",
            "Message": "[MyPlugin]: Finished executing plug-in instance. time: 4.0s.",
        },
    ]
    return pd.DataFrame(data)


def test_extract_plugin_name():
    msg = "Started executing plug-in instance PluginX"
    assert LogParser.extract_plugin_name(msg) == "Started executing plug-in instance"


def test_extract_time_taken():
    msg = "[PluginX]: Finished executing plug-in instance. time: 3.5s."
    assert LogParser.extract_time_taken(msg) == 3.5

    msg2 = "Finished but missing time"
    assert LogParser.extract_time_taken(msg2) is None


def test_filter_relevant_logs(sample_plugin_logs):
    parser = LogParser(sample_plugin_logs)
    df = parser.filter_relevant_logs()
    assert len(df) == len(sample_plugin_logs)
    # All messages match important patterns


def test_find_plugin_times(sample_plugin_logs):
    parser = LogParser(sample_plugin_logs)
    read_secs, exec_secs, write_secs = parser.find_plugin_times(
        sample_plugin_logs.copy()
    )

    assert read_secs == 1  # 05:00:01 - 05:00:00
    assert exec_secs == 2  # 05:00:03 - 05:00:01
    assert write_secs == 1  # 05:00:04 - 05:00:03


def test_find_all_plugins(sample_plugin_logs):
    parser = LogParser(sample_plugin_logs)
    relevant = parser.filter_relevant_logs()
    plugins = parser.find_all_plugins(relevant)

    assert len(plugins) == 1
    plugin = plugins[0]

    assert plugin["PluginName"] == "Started executing plug-in instance"
    assert plugin["TimeTaken (Seconds)"] == 4.0
    assert plugin["IsError"] is False
    assert isinstance(plugin["Data"], DataFrame)
    assert plugin["StartIndex"] == 0
    assert plugin["EndIndex"] == 3


def test_parse_end_to_end(sample_plugin_logs):
    parser = LogParser(sample_plugin_logs)
    result = parser.parse()

    assert len(result) == 1
    p = result[0]

    assert p["IsError"] is False
    assert p["TimeTaken (Seconds)"] == 4.0
