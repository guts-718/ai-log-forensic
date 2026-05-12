from fastapi import APIRouter
import time

from src.pipeline.run_pipeline import run

from src.graph.graph_builder import (
    build_event_graph
)

from src.graph.path_extractor import (
    extract_suspicious_paths
)

from src.graph.subgraph_extractor import (
    build_attack_subgraph
)


router = APIRouter()

# -----------------------------------
# SIMPLE IN-MEMORY CACHE
# -----------------------------------
GRAPH_CACHE = {}


# -----------------------------------
# GRAPH API
# -----------------------------------
@router.get("/graph")
def get_graph():

    # -----------------------------------
    # RETURN CACHED GRAPH
    # -----------------------------------
    if "graph" in GRAPH_CACHE:

        print("Returning cached graph")

        return GRAPH_CACHE["graph"]

    # -----------------------------------
    # LOAD DATA
    # -----------------------------------
    print("Loading data...")

    t = time.time()

    sequences = run()

    print(
        "Data loading completed:",
        round(time.time() - t, 2),
        "seconds"
    )

    # -----------------------------------
    # FLATTEN EVENTS
    # -----------------------------------
    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    # smaller subset for visualization
    events = events[:1000]

    print(
        f"Using {len(events)} events"
    )

    # -----------------------------------
    # BUILD GRAPH
    # -----------------------------------
    print("Building graph...")

    t = time.time()

    G = build_event_graph(events)

    print(
        "Graph build completed:",
        round(time.time() - t, 2),
        "seconds"
    )

    print(
        f"Nodes: {G.number_of_nodes()}"
    )

    print(
        f"Edges: {G.number_of_edges()}"
    )

    # -----------------------------------
    # EXTRACT PATHS
    # -----------------------------------
    print(
        "Extracting suspicious paths..."
    )

    t = time.time()

    suspicious_paths = extract_suspicious_paths(
        G,
        depth=4
    )

    print(
        "Path extraction completed:",
        round(time.time() - t, 2),
        "seconds"
    )

    print(
        f"Found {len(suspicious_paths)} suspicious paths"
    )

    # -----------------------------------
    # USER-DIVERSE PATH SELECTION
    # -----------------------------------
    unique_users = set()

    filtered_paths = []

    for p in suspicious_paths:

        path = p["path"]

        users = set()

        for node in path:

            node_data = G.nodes[node]

            if node_data.get("user"):

                users.add(
                    node_data["user"]
                )

        if not users:
            continue

        user = list(users)[0]

        if user not in unique_users:

            unique_users.add(user)

            filtered_paths.append(p)

    suspicious_paths = filtered_paths[:30]

    print(
        f"Selected {len(suspicious_paths)} diversified paths"
    )

    # -----------------------------------
    # BUILD ATTACK SUBGRAPH
    # -----------------------------------
    print(
        "Building attack subgraph..."
    )

    t = time.time()

    SG = build_attack_subgraph(
        G,
        suspicious_paths
    )

    print(
        "Subgraph build completed:",
        round(time.time() - t, 2),
        "seconds"
    )

    print(
        f"Subgraph nodes: {SG.number_of_nodes()}"
    )

    print(
        f"Subgraph edges: {SG.number_of_edges()}"
    )

    # -----------------------------------
    # SERIALIZE NODES
    # -----------------------------------
    nodes = []

    for node, data in SG.nodes(data=True):

        nodes.append({

            "id": node,

            "label": data.get(
                "event_type",
                data.get("node_type")
            ),

            "type": data.get(
                "node_type"
            ),

            "user": data.get(
                "user"
            ),

            "timestamp": str(
                data.get("timestamp")
            ),

            "risk_score": data.get(
                "risk_score",
                0
            ),
            "resource": data.get(
                "resource"
            ),

            "device": data.get(
                "device"
            ),

            "metadata": data.get(
                "metadata",
                {}
            )
        })

    # -----------------------------------
    # SERIALIZE EDGES
    # -----------------------------------
    edges = []

    for u, v, data in SG.edges(data=True):

        edges.append({

            "source": u,

            "target": v,

            "edge_type": data.get(
                "edge_type"
            ),

            "weight": data.get(
                "weight",
                1
            )
        })

    # -----------------------------------
    # FINAL RESPONSE
    # -----------------------------------
    response = {

        "num_nodes": len(nodes),

        "num_edges": len(edges),

        "nodes": nodes,

        "edges": edges
    }

    # -----------------------------------
    # CACHE GRAPH
    # -----------------------------------
    GRAPH_CACHE["graph"] = response

    print("Graph cached successfully")

    return response