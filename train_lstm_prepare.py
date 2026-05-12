from src.pipeline.run_pipeline import run
from src.lstm.contextual_enricher import (enrich_sequence)
from src.graph.graph_builder import (build_event_graph)
from src.graph.path_extractor import (extract_suspicious_paths)
from src.lstm.sequence_builder import (build_sequence_dataset)
from src.lstm.tokenizer import (build_vocab,encode_sequence)
from src.lstm.preprocessing import (pad_sequences)


def main():

    print("Loading data...")
    sequences = run()
    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    events = events[:30000]
    print("Building graph...")
    G = build_event_graph(events)
    print("Extracting paths...")

    suspicious_paths = extract_suspicious_paths(G,depth=6)

    print(
    "Suspicious paths:",
    len(suspicious_paths)
)

    if suspicious_paths:

        print(
            suspicious_paths[0]
        )


    suspicious_paths = suspicious_paths[:3000]

    print("Building sequence dataset...")

    dataset = build_sequence_dataset(
        G,
        suspicious_paths
    )


    print(
    "Dataset size:",
    len(dataset)
)

    if dataset:

        print(
            dataset[0]
        )

    print(
        f"Total sequences: {len(dataset)}"
    )

    for item in dataset:
        item["sequence"] = enrich_sequence(
            item["sequence"]
        )

    vocab = build_vocab(dataset)

    print(
        f"Vocabulary size: {len(vocab)}"
    )

    X = []

    y = []

    for item in dataset:
        item["sequence"] = enrich_sequence(
            item["sequence"]
        )
        encoded = encode_sequence(
            item["sequence"],
            vocab
        )

        X.append(encoded)

        y.append(item["label"])

    X = pad_sequences(
        X,
        max_len=10
    )

    print(
        "Dataset shape:",
        X.shape
    )

    print(
        "Labels:",
        len(y)
    )

    print(
        "Sample sequence:"
    )

    print(dataset[0])

    print(
        "Encoded:"
    )

    print(X[0])


if __name__ == "__main__":

    main()