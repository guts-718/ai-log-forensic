from .base_event import create_event

def parse_email(df):
    events = []

    for _, row in df.iterrows():
        event = create_event(
            timestamp=row["date"],
            user=row["user"],
            event_type="email",
            metadata={
                "to": row.get("to"),
                "size": row.get("size")
            }
        )
        events.append(event)

    return events