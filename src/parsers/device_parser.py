from .base_event import create_event

def parse_device(df):
    events = []

    for _, row in df.iterrows():
        event = create_event(
            timestamp=row["date"],
            user=row["user"],
            event_type="device",
            device=row.get("device"),
            metadata={
                "activity": row.get("activity")
            }
        )
        events.append(event)

    return events