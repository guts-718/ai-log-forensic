from collections import defaultdict

def build_sequences(events):
    user_events = defaultdict(list)

    # group
    for e in events:
        user_events[e["user"]].append(e)

    # sort
    for user in user_events:
        user_events[user] = sorted(
            user_events[user],
            key=lambda x: x["timestamp"]
        )

    return user_events