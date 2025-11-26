from statistics import mean

import streamlit as st

from pandas import read_csv, DataFrame, options
from app.log_parser import LogParser

st.title("🫧 Log Parser For Plugins")

uploaded_file = st.file_uploader("Upload a log file (csv)", type="csv")


if uploaded_file:
    try:
        log_data = read_csv(uploaded_file, on_bad_lines="warn")
        parser = LogParser(log_data)
        plugins = parser.parse()

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
                        if (
                            row[parser.LEVEL] == "WARN"
                            or row[parser.LEVEL] == "WARNING"
                        ):
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
        import traceback

        traceback.print_exc()
        st.error(f"❌ Failed to parse log: {e}")
else:
    st.info("📁 Please upload a CSV log file to begin.")
