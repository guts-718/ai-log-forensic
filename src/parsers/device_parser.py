from .base_event import create_event

from src.enrichment.semantic_enricher import (
    enrich_event
)


def parse_device(df):

    events = []

    for _, row in df.iterrows():

        activity = str(
            row.get("activity", "")
        ).lower()

        if "connect" in activity:

            event_type = "usb_insert"

        elif "disconnect" in activity:

            event_type = "usb_remove"

        else:

            event_type = "device_activity"

        timestamp = row["date"]

        hour = timestamp.hour

        if hour < 6 or hour > 20:

            event_type = (
                "after_hours_" + event_type
            )

        event = create_event(
            timestamp=timestamp,
            user=row["user"],
            event_type=event_type,
            device=row.get("device"),
            metadata={
                "activity": row.get("activity")
            }
        )
        events.append(event)

    return events