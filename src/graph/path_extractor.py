import networkx as nx

from src.graph.template_matcher import match_all_templates
from src.graph.contextual_scoring import (
    compute_contextual_score
)

MAX_PATHS = 5000


# -----------------------------------
# SUSPICIOUS EVENTS
# -----------------------------------
SUSPICIOUS_EVENTS = {
    "external_transfer",
    "archive_creation",
    "encryption_activity",
    "privilege_escalation"
}


# -----------------------------------
# EDGE SCORE
# -----------------------------------
def edge_score(edge_data):

    return edge_data.get("weight", 1)


# -----------------------------------
# RELATEDNESS
# -----------------------------------
def events_are_related(e1, e2):

    # same user
    if e1.get("user") == e2.get("user"):
        return True

    # same resource
    if (
        e1.get("resource")
        and e1.get("resource") == e2.get("resource")
    ):
        return True

    # same device
    if (
        e1.get("device")
        and e1.get("device") == e2.get("device")
    ):
        return True

    return False


# -----------------------------------
# PATH SCORE
# -----------------------------------
def compute_path_score(G, path):

    total = 0

    for i in range(len(path) - 1):

        u = path[i]
        v = path[i + 1]

        edges = G.get_edge_data(u, v)

        if not edges:
            continue

        # MultiDiGraph support
        for _, edge_data in edges.items():

            total += edge_score(edge_data)

    return total


# -----------------------------------
# EXTRACT SUSPICIOUS PATHS
# -----------------------------------
def extract_suspicious_paths(
    G,
    min_length=3,
    min_score=5,
    depth=6,
    top_neighbors=3
):

    suspicious_paths = []
    seen_signatures = set()

    # suspicious starting nodes only
    event_nodes = [

        n for n, d in G.nodes(data=True)

        if (
            d.get("node_type") == "event"
            and d.get("event_type") in SUSPICIOUS_EVENTS
        )
    ]

    print(
        f"Suspicious anchors: "
        f"{len(event_nodes)}"
    )

    # -----------------------------------
    # DFS TRAVERSAL
    # -----------------------------------
    for start in event_nodes:

        stack = [(start, [start])]

        while stack:

            current, path = stack.pop()

            current_data = G.nodes[current]

            neighbor_scores = []

            # -----------------------------------
            # SCORE NEIGHBORS
            # -----------------------------------
            for neighbor in G.successors(current):

                if neighbor in path:
                    continue

                edge_data = G.get_edge_data(
                    current,
                    neighbor
                )

                score = 0

                if edge_data:

                    for _, ed in edge_data.items():

                        score += ed.get(
                            "weight",
                            1
                        )

                neighbor_scores.append(
                    (neighbor, score)
                )

            # keep top suspicious neighbors only
            neighbor_scores = sorted(
                neighbor_scores,
                key=lambda x: x[1],
                reverse=True
            )[:top_neighbors]

            neighbors = [
                n for n, _ in neighbor_scores
            ]

            # -----------------------------------
            # PROCESS NEIGHBORS
            # -----------------------------------
            for neighbor in neighbors:

                neighbor_data = G.nodes[neighbor]

                t1 = current_data.get("timestamp")
                t2 = neighbor_data.get("timestamp")

                if t1 and t2:

                    diff = abs(
                        (t2 - t1).total_seconds()
                    )

                    # max 10 minute jump
                    if diff > 600:
                        continue

                # maintain event continuity
                if (
                    neighbor_data.get("node_type")
                    == "event"
                ):

                    if not events_are_related(
                        current_data,
                        neighbor_data
                    ):
                        continue

                new_path = path + [neighbor]

                # compute path score
                edge_score = compute_path_score(
                    G,
                    new_path
                )

                context_score = compute_contextual_score(
                    G,
                    new_path
                )

                score = (
                    edge_score
                    + context_score
                )

                # keep suspicious paths
                if (
                    len(new_path) >= 3
                    and score >= 5
                ):

                    # -----------------------------------
                    # CREATE BEHAVIORAL SIGNATURE
                    # -----------------------------------
                    signature = []

                    for n in new_path:

                        d = G.nodes[n]

                        if d.get("node_type") == "event":

                            signature.append(
                                d.get("event_type")
                            )

                    signature = tuple(signature)

                    # -----------------------------------
                    # SKIP DUPLICATES
                    # -----------------------------------
                    if signature in seen_signatures:
                        continue

                    seen_signatures.add(signature)

                    suspicious_paths.append({
                        "path": new_path,
                        "score": score
                    })

                # continue DFS
                if len(new_path) < depth:

                    stack.append(
                        (neighbor, new_path)
                    )

    # -----------------------------------
    # SORT FINAL RESULTS
    # -----------------------------------
    suspicious_paths = sorted(
        suspicious_paths,
        key=lambda x: x["score"],
        reverse=True
    )

    return suspicious_paths