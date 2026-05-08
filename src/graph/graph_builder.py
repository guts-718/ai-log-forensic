import networkx as nx

from src.graph.edge_rules import compute_edge_weight


# -----------------------------
# BUILD FORENSIC GRAPH
# -----------------------------
def build_event_graph(events):

    G = nx.MultiDiGraph()

    # sort by timestamp
    events = sorted(
        events,
        key=lambda x: x.get("timestamp")
    )

    # -----------------------------
    # CREATE NODES
    # -----------------------------
    for idx, event in enumerate(events):

        event_id = f"evt_{idx}"

        event["event_id"] = event_id

        # EVENT NODE
        G.add_node(
            event_id,
            node_type="event",
            **event
        )

        # USER NODE
        user = event.get("user")

        if user:
            G.add_node(
                user,
                node_type="user"
            )

            G.add_edge(
                user,
                event_id,
                edge_type="performed",
                weight=1
            )

        # RESOURCE NODE
        resource = event.get("resource")

        if resource:
            resource_id = f"file_{resource}"

            G.add_node(
                resource_id,
                node_type="file",
                name=resource
            )

            G.add_edge(
                event_id,
                resource_id,
                edge_type="accessed",
                weight=2
            )

        # DEVICE NODE
        device = event.get("device")

        if device:
            device_id = f"device_{device}"

            G.add_node(
                device_id,
                node_type="device",
                name=device
            )

            G.add_edge(
                event_id,
                device_id,
                edge_type="used_device",
                weight=2
            )

    # -----------------------------
    # TEMPORAL + CORRELATION EDGES
    # -----------------------------
    for i in range(len(events) - 1):

        e1 = events[i]
        e2 = events[i + 1]

        id1 = e1["event_id"]
        id2 = e2["event_id"]

        # TEMPORAL EDGE
        G.add_edge(
            id1,
            id2,
            edge_type="temporal",
            weight=1
        )

        # CORRELATION EDGE
        correlation_weight = compute_edge_weight(e1, e2)

        if correlation_weight >= 3:

            G.add_edge(
                id1,
                id2,
                edge_type="correlated",
                weight=correlation_weight
            )

    return G