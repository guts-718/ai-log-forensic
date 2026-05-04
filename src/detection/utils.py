import pandas as pd
from collections import defaultdict

def group_events_by_user(events):
    user_map = defaultdict(list)
    for e in events:
        user_map[e["user"]].append(e)
    return user_map


def create_time_windows(events, window="1H"):
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)

    windows = []

    for _, group in df.groupby(pd.Grouper(freq=window)):
        if len(group) == 0:
            continue
        windows.append(group.reset_index().to_dict("records"))

    return windows