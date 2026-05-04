import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = ["logon.csv", "file.csv", "email.csv", "device.csv"]

def get_top_users(file_path, user_col="user", n=5):
    df = pd.read_csv(file_path, usecols=[user_col])
    top_users = df[user_col].value_counts().head(n).index.tolist()
    return top_users

def filter_file(file_name, top_users, user_col="user"):
    file_path = RAW_DIR / file_name
    out_path = OUT_DIR / file_name.replace(".csv", "_small.csv")

    chunks = pd.read_csv(file_path, chunksize=50000)

    filtered_chunks = []
    for chunk in chunks:
        chunk = chunk[chunk[user_col].isin(top_users)]
        filtered_chunks.append(chunk)

    df_small = pd.concat(filtered_chunks)
    df_small.to_csv(out_path, index=False)

    print(f"Saved: {out_path} | Rows: {len(df_small)}")

def main():
    print("🔍 Finding top users from logon.csv...")
    top_users = get_top_users(RAW_DIR / "logon.csv")

    print("Top users:", top_users)

    for file in FILES:
        print(f"\nProcessing {file}...")
        filter_file(file, top_users)

if __name__ == "__main__":
    main()