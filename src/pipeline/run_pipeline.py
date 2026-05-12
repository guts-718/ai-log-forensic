from pathlib import Path
import pandas as pd
from src.data_loader.loader import load_csv
from src.parsers.logon_parser import parse_logon
from src.parsers.file_parser import parse_file
from src.parsers.email_parser import parse_email
from src.parsers.device_parser import parse_device
from src.normalization.normalizer import normalize_events
from src.sequence.builder import build_sequences
from src.processing.event_mapper import enrich_events

# DATA_DIR = Path("data/processed")
# DATA_DIR = Path("data/raw")


from src.config import DATA_DIR

path = f"{DATA_DIR}/logon.csv"
def run():
    print("Loading data...")

    logon = load_csv(DATA_DIR / "logon.csv")
    file = load_csv(DATA_DIR / "file.csv")
    email = load_csv(DATA_DIR / "email.csv")
    device = load_csv(DATA_DIR / "device.csv")

    # logon = load_csv(DATA_DIR / "logon_small.csv")
    # file = load_csv(DATA_DIR / "file_small.csv")
    # email = load_csv(DATA_DIR / "email_small.csv")
    # device = load_csv(DATA_DIR / "device_small.csv")
    
    logon["date"] = pd.to_datetime(logon["date"])
    file["date"] = pd.to_datetime(file["date"])
    email["date"] = pd.to_datetime(email["date"])
    device["date"] = pd.to_datetime(device["date"])
    print("Parsing...")

    events = []
    events += parse_logon(logon)
    events += parse_file(file)
    events += parse_email(email)
    events += parse_device(device)

    print(f"Total events: {len(events)}")

    print("Normalizing...")
    # fixing timestamps
    events = normalize_events(events) 
    
    events = enrich_events(events)
    print("Building sequences...")
    sequences = build_sequences(events)  # This function groups events by user and sorts each user’s events chronologically based on timestamp. 

    print(f"Total users: {len(sequences)}")

    # quick sanity print
    for user, seq in list(sequences.items())[:2]:
        print(f"\nUser: {user}, Events: {len(seq)}")
        sample_user = next(iter(sequences))
        print("sample user from run_pipeline:\n\n")

        print(
            sequences[sample_user][:20]
        )
        print(seq[:3])
        

    
    from collections import Counter

    print(
        Counter(
            e["event_type"]
            for e in events
        )
    )

    return sequences


if __name__ == "__main__":
    run()