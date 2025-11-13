from pandas import read_csv
from itertools import combinations
import streamlit as st

# --- Streamlit Page Setup ---
# st.set_page_config(page_title="Hierarchy Detector", page_icon="📊", layout="wide")

st.title("📊 Hierarchy Detector")
st.caption(
    "Automatically detect one-to-many or many-to-one relationships between columns in your dataset."
)

# --- Constants ---
ONE_TO_ONE = "ONE_TO_ONE"
ONE_TO_MANY = "ONE_TO_MANY"
MANY_TO_ONE = "MANY_TO_ONE"
NO_RELATION = "NO_RELATION"

st.info(
    "💡 **Tip:** Use smaller datasets for faster detection.\n\n"
    "Each relationship is checked using pairwise column analysis."
)

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")


def get_relation(_data, _left, _right):
    """
    Get relationship between From and To column provided in the params
    """
    first_max = _data.groupby(_left).count().max().iloc[0]
    second_max = _data.groupby(_right).count().max().iloc[0]

    if first_max == 1 and second_max == 1:
        return ONE_TO_ONE
    elif first_max == 1:
        return MANY_TO_ONE  # left → right
    elif second_max == 1:
        return ONE_TO_MANY  # right → left
    else:
        return NO_RELATION


def build_hierarchy(_df):
    adjacency = {col: set() for col in _df.columns}
    attributes = []
    for left, right in combinations(_df.columns, 2):
        relation = get_relation(_df[[left, right]].drop_duplicates(), left, right)
        if relation == ONE_TO_MANY:
            adjacency[left].add(right)
        elif relation == MANY_TO_ONE:
            adjacency[right].add(left)
        elif relation == ONE_TO_ONE:
            attributes.append((left, right))
        # print(">>", left, right, relation)
    return adjacency, attributes


def extract_chains(adjacency):
    reverse_edges = {n: set() for n in adjacency}
    for src, tgts in adjacency.items():
        for tgt in tgts:
            reverse_edges[tgt].add(src)

    roots = [n for n in adjacency if not reverse_edges[n]]
    chains = []

    def dfs(node, path):
        if not adjacency[node]:
            chains.append(path)
            return
        for nxt in adjacency[node]:
            if nxt not in path:
                dfs(nxt, path + [nxt])

    for root in roots:
        dfs(root, [root])
    return [c for c in chains if len(c) > 1]


# --- File Handling and Output ---
if uploaded_file is not None:
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
