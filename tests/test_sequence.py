from src.sequence.builder import build_sequences

def test_sequence_sorting():
    events = [
        {"user": "A", "timestamp": "2024-01-02"},
        {"user": "A", "timestamp": "2024-01-01"},
    ]

    import pandas as pd
    for e in events:
        e["timestamp"] = pd.to_datetime(e["timestamp"])

    seq = build_sequences(events)

    assert seq["A"][0]["timestamp"] < seq["A"][1]["timestamp"]