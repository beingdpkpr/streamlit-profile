import streamlit as st
import re
from pandas import read_csv, DataFrame, options, to_datetime, isna
from statistics import mean

st.title("🫧 Log Parser For Plugins")


options.mode.chained_assignment = None


class LogParser:
    def __init__(self, logs, is_warn: bool = False):
        self.logs: DataFrame = logs
        self.is_warn: bool = is_warn
        self.MESSAGE: str = "Message"
        self.LEVEL: str = "Level"
        self.ERROR: str = "ERROR"
        self.WARN: str = "WARN"
        self.DATA: str = "Data"
        self.TIMESTAMP: str = "Timestamp"
        self.READ_TIME: str = "Read Time"
        self.EXEC_TIME: str = "User Script Time"
        self.WRITE_TIME: str = "Write Time"

        self.plugin_name: str = "PluginName"
        self.start_index: str = "StartIndex"
        self.end_index: str = "EndIndex"
        self.time_taken: str = "TimeTaken (Seconds)"
        self.is_error: str = "IsError"

        # Pre-compile regex patterns
        self._start_pattern = re.compile(
            r"Started executing plug-in instance", re.IGNORECASE
        )
        self._end_pattern = re.compile(
            r"Finished executing plug-in instance", re.IGNORECASE
        )
        # Cache filtered dataframes
        self._start_filter = None
        self._end_filter = None
        self.imp_messages: list[str] = [
            "exec plugin instance",
            self._start_pattern,
            "Data Extractor Query:",
            "Using O9SparkExecutor executor with",
            "Input data keys:",
            "Started executing the script on",
            "script_params=",
            "Starting user code execution",
            "Executing user-defined function.",
            "Importing module :",
            "Successfully executed user-defined function.",
            "dataframe is missing",
            "Storing results back to memcache",
            "Finished Medium Weight script execution on",
            r"Status of the (.+?) plugin run: (\w+)",
            "Name of measures uploaded:",
            "Summary :",
            "Ingestor Result:",
            "Total output rows processed",
            self._end_pattern,
        ]

    def parse(self):
        """Parse logs."""
        relevant_logs = self.filter_relevant_logs()
        return self.find_all_plugins(relevant_logs)

    def _get_start_filter(self, logs) -> DataFrame:
        """Cache and return start filter."""
        if self._start_filter is None:
            self._start_filter = logs[
                logs[self.MESSAGE].str.contains(self._start_pattern, na=False)
            ]
        return self._start_filter

    def _get_end_filter(self, logs) -> DataFrame:
        """Cache and return end filter."""
        if self._end_filter is None:
            self._end_filter = logs[
                logs[self.MESSAGE].str.contains(self._end_pattern, na=False)
            ]
        return self._end_filter

    @staticmethod
    def extract_plugin_name(message: str) -> str | None:
        """Extract plugin name from log message."""
        parts = message.split("]:", 1)
        return parts[1].strip() if len(parts) > 1 else None

    @staticmethod
    def extract_time_taken(message: str) -> float | None:
        """Extract time taken from log message."""
        if "time:" not in message:
            return None
        try:
            return float(message.split("time:", 1)[1].replace("s.", "").strip())
        except (IndexError, ValueError):
            return None

    def filter_relevant_logs(self) -> DataFrame:
        """Filter relevant logs."""
        # Build combined regex pattern
        pattern_parts = []
        for msg in self.imp_messages:
            if isinstance(msg, re.Pattern):
                pattern_parts.append(msg.pattern)
            else:
                # Check if it's already a regex (contains regex special chars)
                if any(c in msg for c in r"()[]{}+*?.|^$\\"):
                    pattern_parts.append(msg)
                else:
                    pattern_parts.append(re.escape(msg))

        important_pattern = re.compile("|".join(pattern_parts), re.IGNORECASE)

        # Single filter: errors OR important messages
        if self.is_warn:
            mask = (
                (self.logs[self.LEVEL] == self.ERROR)
                | (self.logs[self.MESSAGE].str.contains(important_pattern, na=False))
                | (self.logs[self.LEVEL] == self.WARN)
            )
        else:
            mask = (self.logs[self.LEVEL] == self.ERROR) | (
                self.logs[self.MESSAGE].str.contains(important_pattern, na=False)
            )
        relevant_logs = self.logs[mask].copy()
        return relevant_logs

    def find_all_plugins(self, logs) -> list:
        """Find all plugin execution sessions."""
        plugin_detail: list = []
        start_filter = self._get_start_filter(logs)
        end_filter = self._get_end_filter(logs)
        # Create lookup dictionary for faster end matching
        end_messages = end_filter[self.MESSAGE].to_dict()
        used_end_indices = set()
        for start_idx, row in start_filter.iterrows():
            message = str(row[self.MESSAGE])
            plugin_name = self.extract_plugin_name(message)

            if not plugin_name:
                print(f"⚠ Could not extract plugin name: {message}")
                continue
            # Find matching end index
            end_idx = None
            time_taken_val = None
            plugin_logs = DataFrame()
            is_error = False
            read_secs, exec_secs, write_secs = None, None, None
            # Vectorized filtering for candidate ends
            plugin_pattern = re.escape(plugin_name)
            candidate_ends = end_filter[
                (end_filter.index > start_idx)
                & (~end_filter.index.isin(used_end_indices))
                & (
                    end_filter[self.MESSAGE].str.contains(
                        plugin_pattern, case=False, na=False
                    )
                )
            ]
            if not candidate_ends.empty:
                end_idx = candidate_ends.index[0]
                used_end_indices.add(end_idx)
                time_taken_val = self.extract_time_taken(str(end_messages[end_idx]))

                plugin_logs = logs[(logs.index >= start_idx) & (logs.index <= end_idx)]
                if plugin_logs.empty:
                    print(f"No logs for: {plugin_name}.")
                    continue
                is_error = (
                    True if self.ERROR in plugin_logs[self.LEVEL].unique() else False
                )
                read_secs, exec_secs, write_secs = self.find_plugin_times(plugin_logs)

            plugin_detail.append(
                {
                    self.plugin_name: plugin_name,
                    self.start_index: start_idx,
                    self.end_index: end_idx,
                    self.time_taken: time_taken_val,
                    self.is_error: is_error,
                    self.DATA: plugin_logs,
                    self.READ_TIME: read_secs,
                    self.EXEC_TIME: exec_secs,
                    self.WRITE_TIME: write_secs,
                }
            )
        return plugin_detail

    def find_plugin_times(self, logs):
        """Find all plugin execution sessions."""
        logs[self.TIMESTAMP] = to_datetime(logs[self.TIMESTAMP])
        first_ts = logs[self.TIMESTAMP].iloc[0]
        last_ts = logs[self.TIMESTAMP].iloc[-1]
        msgs = logs[self.MESSAGE]
        read_str = [
            "Starting user code execution",
            "Started executing the script on",
            "Importing module :",
            "Executing user-defined function.",
        ]
        exec_str = [
            "Successfully executed user-defined function.",
            "Storing results back to memcache",
            "Finished Medium Weight script execution on",
            r"Status of the (.+?) plugin run: (\w+)",
        ]
        # Status of the SupplyPlan0600PostAnalytics_Inventory_Weekly_Post plugin run: ERROR
        read_mask = msgs.str.contains("|".join(map(re.escape, read_str)))
        exec_mask = msgs.str.contains("|".join(map(re.escape, exec_str)))
        # Pick FIRST occurrence
        # print(first_ts)
        # print("-----------")
        # print(logs.loc[read_mask, (self.TIMESTAMP, self.MESSAGE)])
        read_time = logs.loc[read_mask, self.TIMESTAMP].min()
        exec_time = logs.loc[exec_mask, self.TIMESTAMP].min()

        read_time = None if isna(read_time) else read_time
        exec_time = None if isna(exec_time) else exec_time

        # Convert differences to seconds safely
        read_secs = (read_time - first_ts).total_seconds() if read_time else None
        exec_secs = (
            (exec_time - read_time).total_seconds() if read_time and exec_time else None
        )
        write_secs = (last_ts - exec_time).total_seconds() if exec_time else None

        return read_secs, exec_secs, write_secs


uploaded_file = st.file_uploader("Upload a log file (csv)", type="csv")


if uploaded_file:
    try:
        with st.spinner("🔍 Reading Logs"):
            log_data = read_csv(uploaded_file, on_bad_lines="warn")
        with st.spinner("🔍 Parsing Logs"):
            parser = LogParser(log_data)
            plugins = parser.parse()

        total_plugins = len(plugins)
        failed_plugins = sum(d[parser.is_error] for d in plugins)
        total_time = sum(d[parser.time_taken] for d in plugins)
        avg_time = mean(d[parser.time_taken] for d in plugins)

        # Display summary metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Plugins", total_plugins)
        with col2:
            st.metric("⛔ Failed", failed_plugins)
        with col3:
            st.metric("⏱️ Total Time", f"{total_time:.2f}s" if total_time else "N/A")
        with col4:
            st.metric("⚡ Avg Time", f"{avg_time:.2f}s" if avg_time else "N/A")
        st.markdown("---")
        st.subheader(f"Plugin Summary")
        with st.expander(f"Plugin Summary", expanded=True):
            df = DataFrame(plugins)

            st.dataframe(
                df[
                    [
                        parser.plugin_name,
                        parser.is_error,
                        parser.READ_TIME,
                        parser.EXEC_TIME,
                        parser.WRITE_TIME,
                        parser.time_taken,
                    ]
                ]
            )
        st.markdown("---")

        st.subheader(f"Plugin With Errors")
        for plugin in plugins:
            if plugin[parser.is_error]:
                with st.expander(f"{plugin[parser.plugin_name]}", expanded=True):
                    df = plugin[parser.DATA][
                        [parser.TIMESTAMP, parser.LEVEL, parser.MESSAGE]
                    ]

                    def highlight_row(row):
                        if row[parser.LEVEL] == "ERROR":
                            return ["color: #C30B0B"] * len(row)
                        if row[parser.LEVEL] == "WARNING":
                            return ["color: #C3A50D"] * len(row)

                        return [""] * len(row)

                    styled = df.style.apply(highlight_row, axis=1)
                    st.dataframe(styled)

        st.subheader(f"Successful Plugins")
        for plugin in plugins:
            if not plugin[parser.is_error]:
                with st.expander(f"{plugin[parser.plugin_name]}", expanded=False):
                    st.dataframe(
                        plugin[parser.DATA][
                            [parser.TIMESTAMP, parser.LEVEL, parser.MESSAGE]
                        ]
                    )

        st.markdown("---")
    except Exception as e:
        st.error(f"❌ Failed to parse log: {e}")
else:
    st.info("📁 Please upload a CSV log file to begin.")
