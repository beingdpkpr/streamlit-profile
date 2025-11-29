import re

from pandas import DataFrame, to_datetime, isna, options, merge
from app.time_it import timeit

options.mode.chained_assignment = None


class LogParser:
    def __init__(self, logs, is_warn: bool = False):
        self.MESSAGE: str = "Message"
        self.RId: str = "RId"
        self.THREAD: str = "Thread"
        self.LEVEL: str = "Level"
        self.TIMESTAMP: str = "Timestamp"
        self.SERVER: str = "Server"
        # self.LOGGER: str = "Logger"

        input_columns: list = [
            self.RId,
            self.THREAD,
            self.LEVEL,
            # self.LOGGER,
            self.TIMESTAMP,
            self.SERVER,
            self.MESSAGE,
        ]
        # print(logs.columns)
        self.logs: DataFrame = logs[input_columns]
        self.is_warn: bool = is_warn
        self.ERROR: str = "ERROR"
        self.WARN: str = "WARN"
        self.DATA: str = "Data"
        self.READ_TIME: str = "Read Time"
        self.EXEC_TIME: str = "User Script Time"
        self.WRITE_TIME: str = "Write Time"
        self.OUTPUT_MEASURES: str = "Output Measures"
        self.python_plugin_server: str = "PythonPlugin"

        self.plugin_name: str = "PluginName"
        self.start_index: str = "StartIndex"
        self.end_index: str = "EndIndex"
        self.time_taken: str = "Execution Time (Seconds)"
        self.is_error: str = "IsError"

        self._start_pattern = re.compile(
            r"Started executing plug-in instance", re.IGNORECASE
        )
        self._end_pattern = re.compile(
            r"Finished executing plug-in instance", re.IGNORECASE
        )
        # Cache filtered dataframes
        self._start_filter = None
        self._end_filter = None

        self.filtered_log_statements: list[str] = [
            self._start_pattern,
            "Data Extractor Query:",
            "Using O9SparkExecutor executor with",
            "Input data keys:",
            "Started executing the script on",
            "script_params=",
            "Starting Medium Weight script execution",
            "Starting user code execution",
            "Executing user-defined function.",
            "Importing module :",
            "Successfully executed user-defined function.",
            "dataframe is missing",
            "Storing results back to memcache",
            "Finished Medium Weight script execution on",
            "Writing output data to files / tables",
            r"Status of the (.+?) plugin run: (\w+)",
            # "Total Rows:",
            "Name of measures uploaded:",
            # "Summary :",
            # "Ingestor Result:",
            "Total output rows processed",
            "Time taken to upload",
            self._end_pattern,
            "Script did not complete successfully for ",
        ]

    # @timeit
    def parse_plugins(self):
        """Parse logs."""
        relevant_logs = self.filter_relevant_logs()
        # print(relevant_logs[self.MESSAGE])
        return self.find_all_plugins(relevant_logs)

    # @timeit
    def parse_queries(self):
        query_received = "Query Received: {"
        query_finished = "CPU TIME: {"
        duration_mm_ss: str = "Execution Time (mm:ss)"
        unique_id: str = "unique_id"
        start_time_header: str = "Start Executions Time"
        end_time_header: str = "End Executions Time"

        msgs = self.logs[self.MESSAGE]

        # --- Filter start and end logs (vectorized) ---
        start_logs = self.logs[msgs.str.contains(query_received, regex=False, na=False)]
        end_logs = self.logs[msgs.str.contains(query_finished, regex=False, na=False)]

        start_logs = start_logs.assign(
            unique_id=start_logs[self.MESSAGE].str.split(":", n=2).str[1]
        )
        end_split = end_logs[self.MESSAGE].str.split(":", n=3)
        end_logs = end_logs.assign(
            unique_id=end_split.str[1],
            cpu_ms_raw=end_split.str[2].str.replace("ms", "").str.strip(),
        )
        end_logs[self.time_taken] = end_logs["cpu_ms_raw"].astype(float) / 1000
        # --- Join start and end logs on unique_id ---
        merged = merge(
            start_logs,
            end_logs[[unique_id, self.TIMESTAMP, self.time_taken]],
            on=unique_id,
            how="left",
            suffixes=("", "_end"),
        )
        # --- Clean query text (vectorized) ---
        merged[self.MESSAGE] = (
            merged[self.MESSAGE]
            .str.replace(r"Query Received: {.*}:", "", regex=True)
            .str.replace("^", "", regex=False)
            .str.slice(0, 4000)
            .str.strip()
        )
        merged[duration_mm_ss] = (
            (merged[self.time_taken] // 60).astype(int).astype(str).str.zfill(2)
            + ":"
            + (merged[self.time_taken] % 60)
            .round()
            .astype(int)
            .astype(str)
            .str.zfill(2)
        )
        merged[start_time_header] = to_datetime(merged[self.TIMESTAMP])
        merged[end_time_header] = to_datetime(merged[self.TIMESTAMP + "_end"])

        output = DataFrame(
            {
                self.RId: merged[self.RId],
                self.THREAD: merged[self.THREAD],
                self.MESSAGE: merged[self.MESSAGE],
                start_time_header: merged[start_time_header],
                end_time_header: merged[end_time_header],
                self.time_taken: merged[self.time_taken].round(4),
                duration_mm_ss: merged[duration_mm_ss],
            }
        )

        return output.sort_values(by=[self.time_taken], ascending=False)

    # @timeit
    def parse_computations(self):
        INVOCATIONS: str = "Invocations Count"
        EXECUTIONS: str = "Executions Count"
        NO_OPS: str = "No-Operations Count"
        computation_str = "Computation execution time"
        computation_logs = self.logs[
            (
                self.logs[self.MESSAGE].str.contains(
                    computation_str, regex=False, na=False
                )
            )
        ]
        computation_logs[self.time_taken] = (
            computation_logs[self.MESSAGE]
            .str.extract(r"Computation execution time:\s*([\d.]+)\s*s")
            .astype(float)
        )

        computation_logs[self.MESSAGE] = (
            computation_logs[self.MESSAGE]
            .str.replace(
                r"(Finished computation \[\d+\]\. Query :|Computation execution time:\s*[\d.]+\s*s)",
                "",
                regex=True,
            )
            .str.strip()
        )
        computation_logs["index"] = computation_logs.index
        prev_index = computation_logs.index - 1
        prev_logs = self.logs.loc[prev_index]
        prev_logs["index"] = prev_index + 1
        computation_logs = computation_logs.merge(
            prev_logs[["index", self.MESSAGE]],
            on="index",
            how="left",
            suffixes=("", "_end"),
        )
        computation_logs[[INVOCATIONS, EXECUTIONS, NO_OPS]] = computation_logs[
            f"{self.MESSAGE}_end"
        ].str.extract(
            r"invocations:\s*(\d+);\s*executions:\s*(\d+);\s*non-null no ops:\s*(\d+)",
            flags=re.IGNORECASE,
        )
        return computation_logs[
            [
                self.RId,
                self.THREAD,
                self.MESSAGE,
                self.time_taken,
                INVOCATIONS,
                EXECUTIONS,
                NO_OPS,
            ]
        ].sort_values(by=[self.time_taken], ascending=False)

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

    # @timeit
    def filter_relevant_logs(self) -> DataFrame:
        """Filter relevant logs."""
        # Build combined regex pattern
        pattern_parts = []
        for msg in self.filtered_log_statements:
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
        mask = (
            (self.logs[self.LEVEL] == self.ERROR)
            | (self.logs[self.MESSAGE].str.contains(important_pattern, na=False))
            | (self.logs[self.SERVER] == self.python_plugin_server)
        )
        if self.is_warn:
            mask = mask | (self.logs[self.LEVEL] == self.WARN)

        relevant_logs = self.logs[mask].copy()
        return relevant_logs

    # @timeit
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
            rid = row[self.RId]
            # thread = row[self.THREAD]
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
            output_measures = ""
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

                plugin_logs = logs[
                    (logs.index >= start_idx)
                    & (logs.index <= end_idx)
                    & (logs[self.RId] == rid)
                    # & (logs[self.THREAD] == thread)
                ]
                if plugin_logs.empty:
                    print(f"No logs for: {plugin_name}.")
                    continue
                is_error = (
                    True if self.ERROR in plugin_logs[self.LEVEL].unique() else False
                )
                read_secs, exec_secs, write_secs = self.find_plugin_times(plugin_logs)
                output_measures = self.find_output_measures(plugin_logs)

            plugin_detail.append(
                {
                    self.plugin_name: plugin_name,
                    self.start_index: start_idx,
                    self.end_index: end_idx,
                    self.time_taken: time_taken_val,
                    self.is_error: is_error,
                    self.DATA: plugin_logs.drop_duplicates(),
                    self.READ_TIME: read_secs,
                    self.EXEC_TIME: exec_secs,
                    self.WRITE_TIME: write_secs,
                    self.OUTPUT_MEASURES: output_measures,
                }
            )
        return plugin_detail

    def find_output_measures(self, logs) -> str:
        """Find output measurements."""
        output_measures: list = []
        measure_str = ["Name of measures uploaded:"]
        msgs = logs[self.MESSAGE]
        mask = msgs.str.contains("|".join(map(re.escape, measure_str)))
        out_measures_str = logs.loc[mask, self.MESSAGE].unique()
        for measure in out_measures_str:
            measure = (
                measure.replace("Name of measures uploaded:", "").strip().split(",")
            )
            output_measures += measure

        return ", ".join(output_measures)

    # @timeit
    def find_plugin_times(self, logs):
        """Find all plugin execution sessions."""
        logs[self.TIMESTAMP] = to_datetime(logs[self.TIMESTAMP])
        ts = logs[self.TIMESTAMP]

        first_ts = ts.iat[0]
        last_ts = ts.iat[-1]

        msgs = logs[self.MESSAGE]
        read_str = [
            "Starting user code execution",
            "Started executing the script on",
            "Importing module :",
            "Executing user-defined function.",
            "Starting Medium Weight script execution",
        ]
        exec_str = [
            "Successfully executed user-defined function.",
            "Storing results back to memcache",
            "Finished Medium Weight script execution on",
            r"Status of the (.+?) plugin run: (\w+)",
            "Writing output data to files / tables",
        ]
        read_mask = msgs.str.contains("|".join(map(re.escape, read_str)))
        exec_mask = msgs.str.contains("|".join(map(re.escape, exec_str)))

        # read_time = logs.loc[read_mask, self.TIMESTAMP].min()
        # exec_time = logs.loc[exec_mask, self.TIMESTAMP].min()
        read_time = ts[read_mask].min()
        exec_time = ts[exec_mask].min()

        if isna(read_time):
            read_time = None
        if isna(exec_time):
            exec_time = None

        # Convert differences to seconds safely
        read_secs = (read_time - first_ts).total_seconds() if read_time else None
        exec_secs = (
            (exec_time - read_time).total_seconds() if read_time and exec_time else None
        )
        write_secs = (last_ts - exec_time).total_seconds() if exec_time else None

        return read_secs, exec_secs, write_secs


# if __name__ == "__main__":
#     from pandas import read_csv
#
#     df1 = read_csv("log/network spark logs.Csv")
#     parser = LogParser(df1)
#     #     test = parser.parse_plugins()
#     #     print(test[0]["Data"]["Message"])
#     #     test[0]["Data"].to_csv("1.csv", index=False)
#     #     test = parser.parse_queries()
#     test = parser.parse_computations()
#     print(test)
