from src.pipeline.run_pipeline import run

from src.graph.graph_builder import (
    build_event_graph
)

from src.graph.path_extractor import (
    extract_suspicious_paths
)

from src.lstm.sequence_builder import (
    build_lstm_dataset
)

from src.lstm.train_lstm import (
    train_lstm
)


def main():

    print("Loading data...")

    sequences = run()

    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    print(
        f"Events: {len(events)}"
    )

    # -----------------------------------
    # BUILD GRAPH
    # -----------------------------------
    print("Building graph...")

    G = build_event_graph(events[:5000])

    # -----------------------------------
    # EXTRACT PATHS
    # -----------------------------------
    print(
        "Extracting suspicious paths..."
    )

    suspicious_paths = extract_suspicious_paths(
        G,
        depth=4
    )

    print(
    "Suspicious paths:",
    len(suspicious_paths)
)

    if suspicious_paths:

        print(
            suspicious_paths[0]
        )
    suspicious_paths = suspicious_paths[:1000]

    print(
        f"Suspicious paths: "
        f"{len(suspicious_paths)}"
    )

    # -----------------------------------
    # BUILD DATASET
    # -----------------------------------
    print(
        "Building LSTM dataset..."
    )

    X, y = build_lstm_dataset(

        G,
        suspicious_paths,
        events
    )

    print(
        f"Sequences: {len(X)}"
    )

    # -----------------------------------
    # TRAIN
    # -----------------------------------
    print("Training LSTM...")

    train_lstm(X, y)


if __name__ == "__main__":
    main()