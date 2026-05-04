from pathlib import Path

from src.data_loader.loader import load_csv
from src.parsers.logon_parser import parse_logon
from src.parsers.file_parser import parse_file
from src.parsers.email_parser import parse_email
from src.parsers.device_parser import parse_device
from src.normalization.normalizer import normalize_events
from src.sequence.builder import build_sequences

DATA_DIR = Path("data/processed")
# DATA_DIR = Path("data/raw")

def run():
    print("Loading data...")

    # logon = load_csv(DATA_DIR / "logon.csv")
    # file = load_csv(DATA_DIR / "file.csv")
    # email = load_csv(DATA_DIR / "email.csv")
    # device = load_csv(DATA_DIR / "device.csv")

    logon = load_csv(DATA_DIR / "logon_small.csv")
    file = load_csv(DATA_DIR / "file_small.csv")
    email = load_csv(DATA_DIR / "email_small.csv")
    device = load_csv(DATA_DIR / "device_small.csv")

    print("Parsing...")

    events = []
    events += parse_logon(logon)
    events += parse_file(file)
    events += parse_email(email)
    events += parse_device(device)

    print(f"Total events: {len(events)}")

    print("Normalizing...")
    events = normalize_events(events)

    print("Building sequences...")
    sequences = build_sequences(events)

    print(f"Total users: {len(sequences)}")

    # quick sanity print
    for user, seq in list(sequences.items())[:2]:
        print(f"\nUser: {user}, Events: {len(seq)}")
        print(seq[:3])

    return sequences


if __name__ == "__main__":
    run()