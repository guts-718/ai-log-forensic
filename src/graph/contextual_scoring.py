SUSPICIOUS_EVENT_SCORES = {

    "external_transfer": 9,
    "usb_insert": 7,
    "archive_creation": 6,
    "bulk_file_access": 5,
    "failed_logon": 5,
    "privilege_escalation": 10,
    "encryption_activity": 10,

    # lower scores
    "email_sent": 2,
    "successful_logon": 1,
    "file_access": 2,
    "web_activity": 1,
    "process_start": 2
}


# -----------------------------------
# BASE SCORE
# -----------------------------------
def get_base_score(event_type):

    return SUSPICIOUS_EVENT_SCORES.get(
        event_type,
        0
    )


# -----------------------------------
# CONTEXTUAL SCORE
# -----------------------------------
def compute_contextual_score(
    G,
    path
):

    total = 0

    event_nodes = []

    # only event nodes
    for node in path:

        node_data = G.nodes[node]

        if node_data.get("node_type") == "event":

            event_nodes.append(node_data)

    # compute propagation
    for i, event in enumerate(event_nodes):

        event_type = event.get("event_type")

        base = get_base_score(event_type)

        total += base

        # nearby suspicious influence
        for j in range(
            max(0, i - 2),
            min(len(event_nodes), i + 3)
        ):

            if i == j:
                continue

            nearby = event_nodes[j]

            nearby_type = nearby.get(
                "event_type"
            )

            nearby_score = get_base_score(
                nearby_type
            )

            # propagate suspicion
            total += nearby_score * 0.15

    return round(total, 2)