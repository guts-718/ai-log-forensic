import pandas as pd
from collections import defaultdict


def build_user_baselines(events):
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["hour"] = df["timestamp"].dt.floor("H")

    baselines = {}

    for user, group in df.groupby("user"):
        hourly = group.groupby("hour")

        file_counts = []
        email_counts = []
        logon_counts = []

        for _, g in hourly:
            file_counts.append((g["event_type"] == "file").sum())
            email_counts.append((g["event_type"] == "email").sum())
            logon_counts.append((g["event_type"] == "logon").sum())

        baselines[user] = {
            "avg_file": sum(file_counts) / len(file_counts) if file_counts else 0,
            "avg_email": sum(email_counts) / len(email_counts) if email_counts else 0,
            "avg_logon": sum(logon_counts) / len(logon_counts) if logon_counts else 0,
        }

    return baselines