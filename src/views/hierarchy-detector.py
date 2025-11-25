from pandas import read_csv
from itertools import combinations
import streamlit as st
from app.hierarchy import build_hierarchy, extract_chains

# --- Streamlit Page Setup ---
# st.set_page_config(page_title="Hierarchy Detector", page_icon="📊", layout="wide")

st.title("📊 Hierarchy Detector")
st.caption(
    "Automatically detect one-to-many or many-to-one relationships between columns in your dataset."
)

st.info(
    "💡 **Tip:** Use smaller datasets for faster detection.\n\n"
    "Each relationship is checked using pairwise column analysis."
)

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")


# --- File Handling and Output ---
if uploaded_file:
    try:
        with st.spinner("🔍 Analyzing relationships..."):
            df = read_csv(uploaded_file)
            adj, equivalents = build_hierarchy(df)
            chains = extract_chains(adj)

        st.success("✅ Hierarchy detection complete!")

        # --- Search Bar ---
        search_query = (
            st.text_input(
                "🔎 Search hierarchies (by column name):",
                placeholder="Type to filter results...",
            )
            .strip()
            .lower()
        )

        st.markdown("### 📈 Detected Hierarchies")

        if chains:
            filtered_chains = (
                [c for c in chains if any(search_query in col.lower() for col in c)]
                if search_query
                else chains
            )

            if filtered_chains:
                for c in filtered_chains:
                    hierarchy_str = " → ".join(c)
                    # Highlight the search term if present
                    if search_query:
                        for col in c:
                            if search_query in col.lower():
                                hierarchy_str = hierarchy_str.replace(
                                    col,
                                    f"<span style='background-color:#334155;padding:2px 4px;border-radius:4px;'>{col}</span>",
                                )
                    st.markdown(f"- 🔗 {hierarchy_str}", unsafe_allow_html=True)
            else:
                st.warning("No hierarchies match your search query.")
        else:
            st.info(
                "No hierarchical (one-to-many / many-to-one) relationships detected."
            )

        if equivalents:
            with st.expander("🧩 Equivalent (One-to-One) Relationships"):
                for left, right in equivalents:
                    st.write(f"➡️ `{left}` ↔ `{right}`")
        else:
            st.caption("No one-to-one attribute pairs found.")

        st.divider()
        st.caption("Analysis completed successfully ✅")

    except Exception as e:
        st.error("⚠️ Error reading file. Please ensure it's a valid CSV.")
        st.exception(e)

else:
    st.info("👆 Upload a CSV file to begin analysis.")

    with st.expander("💡 Example and Explanation"):
        st.markdown(
            """
        **Relationship Types Explained:**

        | Type | Description | Example |
        |------|--------------|----------|
        | 🔹 One-to-Many | One value maps to multiple values | Country → City |
        | 🔸 Many-to-One | Multiple values map to one value | City → Country |
        | 🔷 One-to-One | One value maps to exactly one value | Employee ID ↔ Name |
        | ⚫ No Relation | No clear mapping between columns | Random columns |
        """
        )
