import pandas as pd
from collections import defaultdict


# -----------------------------
# Build user baselines
# -----------------------------
def build_user_baselines(event_store):
    """
    Builds baseline statistics per user.

    Input:
        event_store: list of normalized events

    Output:
        baselines: dict[user] -> stats
    """

    # -----------------------------
    # Group events by user
    # -----------------------------
    user_events = defaultdict(list)

    for event in event_store:
        user = event.get("user")
        user_events[user].append(event)

    baselines = {}

    # -----------------------------
    # Compute stats per user
    # -----------------------------
    for user, events in user_events.items():

        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(events)

        if df.empty:
            baselines[user] = {}
            continue

        # Count events by type
        file_count = (df["event_type"] == "file").sum()
        email_count = (df["event_type"] == "email").sum()
        logon_count = (df["event_type"] == "logon").sum()

        total_events = len(df)

        # Avoid division issues
        avg_file = file_count / total_events if total_events else 0
        avg_email = email_count / total_events if total_events else 0
        avg_logon = logon_count / total_events if total_events else 0

        # For std, we approximate using per-event indicator vectors
        file_series = (df["event_type"] == "file").astype(int)
        email_series = (df["event_type"] == "email").astype(int)
        logon_series = (df["event_type"] == "logon").astype(int)

        std_file = file_series.std() if len(file_series) > 1 else 1
        std_email = email_series.std() if len(email_series) > 1 else 1
        std_logon = logon_series.std() if len(logon_series) > 1 else 1

        # Prevent zero std
        std_file = std_file if std_file > 0 else 1
        std_email = std_email if std_email > 0 else 1
        std_logon = std_logon if std_logon > 0 else 1

        baselines[user] = {
            "avg_file": avg_file,
            "std_file": std_file,

            "avg_email": avg_email,
            "std_email": std_email,

            "avg_logon": avg_logon,
            "std_logon": std_logon,
        }

    return baselines