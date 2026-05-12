import random


# -----------------------------------
# PATH → EVENT SEQUENCE
# -----------------------------------
def path_to_sequence(
    G,
    path
):

    event_nodes = []

    # -----------------------------------
    # COLLECT EVENT NODES
    # -----------------------------------
    for node in path:

        data = G.nodes[node]

        if data.get("node_type") == "event":

            timestamp = data.get(
                "timestamp"
            )

            event_nodes.append(
                (timestamp, data)
            )

    # -----------------------------------
    # SORT TEMPORALLY
    # -----------------------------------
    event_nodes = sorted(
        event_nodes,
        key=lambda x: x[0]
    )

    sequence = []

    # -----------------------------------
    # BUILD ORDERED SEQUENCE
    # -----------------------------------
    for _, data in event_nodes:

        event_type = data.get(
            "event_type"
        )

        if event_type:

            sequence.append(
                event_type
            )

    return sequence

# -----------------------------------
# BUILD SUSPICIOUS SEQUENCES
# -----------------------------------
def build_suspicious_sequences(
    G,
    suspicious_paths
):

    sequences = []

    for item in suspicious_paths:

        path = item["path"]

        seq = path_to_sequence(
            G,
            path
        )

        if len(seq) >= 3:

            sequences.append({

                "sequence": seq,

                "label": 1
            })

    return sequences


# -----------------------------------
# BUILD BENIGN SEQUENCES
# -----------------------------------
def build_benign_sequences(
    G,
    num_sequences=500
):

    sequences = []

    event_nodes = [

        n for n, d in G.nodes(data=True)

        if d.get("node_type") == "event"
    ]

    for _ in range(num_sequences):

        start = random.choice(
            event_nodes
        )

        seq = []

        current = start

        visited = set()

        depth = random.randint(3, 6)

        for _ in range(depth):

            if current in visited:
                break

            visited.add(current)

            node_data = G.nodes[current]

            event_type = node_data.get(
                "event_type"
            )

            if event_type:

                seq.append(
                    event_type
                )

            neighbors = list(
                G.successors(current)
            )

            if not neighbors:
                break

            current = random.choice(
                neighbors
            )

        if len(seq) >= 3:

            sequences.append({

                "sequence": seq,

                "label": 0
            })

    return sequences


# -----------------------------------
# BUILD FULL DATASET
# -----------------------------------
def build_sequence_dataset(
    G,
    suspicious_paths
):

    suspicious_sequences = (

        build_suspicious_sequences(
            G,
            suspicious_paths
        )
    )

    benign_sequences = (

        build_benign_sequences(
            G,
            num_sequences=len(
                suspicious_sequences
            )*3
        )
    )

    dataset = (
        suspicious_sequences
        + benign_sequences
    )

    random.shuffle(dataset)

    return dataset