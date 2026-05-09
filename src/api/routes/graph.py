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

GRAPH_CACHE = {}
router = APIRouter()


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

    print("Loading data...")
    t = time.time()
    sequences = run()
    print(
    "run done:",
    time.time() - t
    )
    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    # smaller subset initially
    # events = events[:5000]

    events = events[:1000]

    print("Building graph...")
    t = time.time()

    G = build_event_graph(events)

    print(
    "Graph build:",
    time.time() - t
    )

    print("Extracting suspicious paths...")

    suspicious_paths = extract_suspicious_paths(
        G,
        depth=4
    )

    # suspicious_paths = suspicious_paths[:100]
    suspicious_paths = suspicious_paths[:30]

    print("Building attack subgraph...")

    t = time.time()
    SG = build_attack_subgraph(
        G,
        suspicious_paths
    )

    print(
    "Attack subgraph build:",
    time.time() - t
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

            "user": data.get("user"),

            "timestamp": str(
                data.get("timestamp")
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

            "type": data.get(
                "edge_type"
            ),

            "weight": data.get(
                "weight",
                1
            )
        })

    response = {

    "num_nodes": len(nodes),
    "num_edges": len(edges),

    "nodes": nodes,
    "edges": edges
}

    GRAPH_CACHE["graph"] = response

    return response