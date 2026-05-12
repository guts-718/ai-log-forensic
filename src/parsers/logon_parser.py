from .base_event import create_event

from src.enrichment.semantic_enricher import (
    enrich_event
)


def parse_logon(df):

    events = []

    for _, row in df.iterrows():

        activity = str(
            row.get("activity", "")
        ).lower()

        timestamp = row["date"]

        hour = timestamp.hour

        if "logoff" in activity:

            event_type = "logoff"

        elif hour < 6 or hour > 20:

            event_type = (
                "after_hours_logon"
            )

        else:

            event_type = (
                "normal_logon"
            )

        event = create_event(
            timestamp=timestamp,
            user=row["user"],
            event_type=event_type,
            metadata={
                "pc": row.get("pc"),
                "activity": row.get("activity")
            }
        )

        events.append(event)

    return events