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
    event_sequence = list(G.nodes())


    # -----------------------------------
    # COLLECT ALL PATH NODES
    # -----------------------------------
    for path_data in suspicious_paths:

        path = path_data["path"]

        for node in path:
            included_nodes.add(node)

            # -----------------------------------
            # ADD CONTEXT NEIGHBORS
            # -----------------------------------
            neighbors = list(
                G.successors(node)
            )[:2]

            for n in neighbors:
                included_nodes.add(n)

            predecessors = list(
                G.predecessors(node)
            )[:2]

            for p in predecessors:
                included_nodes.add(p)

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
    important_edges = []

    for u, v, data in G.edges(data=True):

        if (
            u in included_nodes
            and v in included_nodes
        ):

            important_edges.append(
                (u, v, data)
            )

    # keep strongest edges
    important_edges = sorted(

        important_edges,

        key=lambda x: x[2].get(
            "weight",
            1
        ),

        reverse=True
    )[:300]

    for u, v, data in important_edges:

        SG.add_edge(
            u,
            v,
            **data
        )

    return SG