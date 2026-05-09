import networkx as nx


# -----------------------------------
# BUILD ATTACK SUBGRAPH
# -----------------------------------
def build_attack_subgraph(
    G,
    suspicious_paths
):

    SG = nx.MultiDiGraph()

    included_nodes = set()

    # -----------------------------------
    # COLLECT ALL PATH NODES
    # -----------------------------------
    for path_data in suspicious_paths:

        path = path_data["path"]

        for node in path:
            included_nodes.add(node)

    # -----------------------------------
    # ADD NODES
    # -----------------------------------
    for node in included_nodes:

        SG.add_node(
            node,
            **G.nodes[node]
        )

    # -----------------------------------
    # ADD CONNECTING EDGES
    # -----------------------------------
    for u, v, data in G.edges(data=True):

        if (
            u in included_nodes
            and v in included_nodes
        ):

            SG.add_edge(
                u,
                v,
                **data
            )

    return SG