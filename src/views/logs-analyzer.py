import streamlit as st
import pandas as pd

from statistics import mean

from app.log_parser import LogParser
from app.time_it import timeit


st.title("🫧 Logs Analyzer")


@timeit
def read_log(_file):
    data = pd.read_csv(
        _file,
        on_bad_lines="skip",
        # low_memory=False,
        engine="python",
        dtype=str,
    )
    return data


uploaded_file = st.file_uploader("Upload a log file (csv)", type="csv")

if uploaded_file:
    plugin_tab, queries_tab = st.tabs(["Plugins", "Queries"])
    try:
        log_data = read_log(uploaded_file)
        parser = LogParser(log_data)
    except Exception as e:
        st.error(f"❌ Failed to parse log: {e}")
        exit(1)

    with plugin_tab:
        plugins = parser.parse_plugins()

        try:
            total_plugins = len(plugins)
            failed_plugins = sum(d[parser.is_error] for d in plugins)
            total_time = sum(d[parser.time_taken] for d in plugins)
            avg_time = mean(d[parser.time_taken] for d in plugins)

        except TypeError:
            print(d[parser.is_error] for d in plugins)
            total_plugins = 0
            failed_plugins = 0
            total_time = 0
            avg_time = 0

        # Display summary metrics
        st.markdown("---")
        st.subheader(f"Summary")
        total_plugin, failed_plugin, total_time_header, avg_time_header = st.columns(4)
        with total_plugin:
            st.metric("📊 Total Plugins", total_plugins)
        with failed_plugin:
            st.metric("⛔ Failed", failed_plugins)
        with total_time_header:
            st.metric("⏱️ Total Time", f"{total_time:.2f}s" if total_time else "N/A")
        with avg_time_header:
            st.metric("⚡ Avg Time", f"{avg_time:.2f}s" if avg_time else "N/A")
        st.markdown("---")

        if len(plugins) > 0:
            st.subheader(f"Plugin Details")
            # with st.expander(f"Plugin Summary", expanded=True):
            df = pd.DataFrame(plugins)
            st.dataframe(
                df[
                    [
                        parser.plugin_name,
                        parser.is_error,
                        parser.READ_TIME,
                        parser.EXEC_TIME,
                        parser.WRITE_TIME,
                        parser.time_taken,
                        parser.OUTPUT_MEASURES,
                    ]
                ].sort_values(by=[parser.time_taken], ascending=False)
            )
            st.markdown("---")

        st.subheader(f"Plugin With Errors")
        all_plugin_success: bool = True
        for plugin_tab in plugins:
            if plugin_tab[parser.is_error]:
                all_plugin_success = False
                with st.expander(f"{plugin_tab[parser.plugin_name]}", expanded=True):
                    df = plugin_tab[parser.DATA][
                        [parser.TIMESTAMP, parser.LEVEL, parser.MESSAGE]
                    ]

                    def highlight_row(row):
                        if row[parser.LEVEL] == "ERROR":
                            return ["color: #C30B0B"] * len(row)
                        if (
                            row[parser.LEVEL] == "WARN"
                            or row[parser.LEVEL] == "WARNING"
                        ):
                            return ["color: #C3A50D"] * len(row)

                        return [""] * len(row)

                    styled = df.style.apply(highlight_row, axis=1)
                    st.dataframe(styled)
        if not all_plugin_success:
            st.subheader(f"Successful Plugins")
            for plugin_tab in plugins:
                if not plugin_tab[parser.is_error]:
                    with st.expander(
                        f"{plugin_tab[parser.plugin_name]}", expanded=False
                    ):
                        st.dataframe(
                            plugin_tab[parser.DATA][
                                [parser.TIMESTAMP, parser.LEVEL, parser.MESSAGE]
                            ]
                        )

        st.markdown("---")
    with queries_tab:
        try:
            queries = parser.parse_queries()
            st.dataframe(queries)

        except Exception as e:
            st.error(f"❌ Failed to parse log: {e}")
            exit(1)
        st.markdown("---")
else:
    st.info("📁 Please upload a CSV log file to begin.")
