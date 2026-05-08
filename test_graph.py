from src.pipeline.run_pipeline import run
from src.graph.graph_builder import build_event_graph


def main():

    sequences = run()

    events = []

    for _, seq in sequences.items():
        events.extend(seq)

    # small subset first
    events = events[:100]

    G = build_event_graph(events)

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    print("\nSample Nodes:")
    print(list(G.nodes(data=True))[:5])

    print("\nSample Edges:")
    print(list(G.edges(data=True))[:10])


if __name__ == "__main__":
    main()