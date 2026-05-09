from src.pipeline.run_pipeline import run

from src.graph.graph_builder import build_event_graph
from src.graph.path_extractor import extract_suspicious_paths
from src.graph.graph_utils import pretty_print_path


def main():

    sequences = run()

    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    # subset first
    events = events[:5000]

    print("Building graph...")

    G = build_event_graph(events)

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    print("\nExtracting suspicious paths...")

    paths = extract_suspicious_paths(
    G,
    depth=4
    )

    print(f"Found {len(paths)} suspicious paths")
    print(paths[:3])
    for p in paths[:5]:
        pretty_print_path(G, p)


if __name__ == "__main__":
    main()