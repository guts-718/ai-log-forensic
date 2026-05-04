from .base_event import create_event

def parse_logon(df):
    events = []

    for _, row in df.iterrows():
        event = create_event(
            timestamp=row["date"],
            user=row["user"],
            event_type="logon",
            metadata={
                "pc": row.get("pc"),
                "activity": row.get("activity")
            }
        )
        events.append(event)

    return events