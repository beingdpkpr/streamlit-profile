from itertools import combinations


# --- Constants ---
ONE_TO_ONE = "ONE_TO_ONE"
ONE_TO_MANY = "ONE_TO_MANY"
MANY_TO_ONE = "MANY_TO_ONE"
NO_RELATION = "NO_RELATION"


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
