from .base_event import create_event

from src.enrichment.semantic_enricher import (
    enrich_event
)


def parse_email(df):

    events = []

    for _, row in df.iterrows():

        to_field = row.get("to", "")

        recipients = str(
            to_field
        ).split(";")

        size = int(
            row.get("size", 0)
        )

        external = any(
            "@dtaa.com" not in r.lower()
            for r in recipients
        )

        if len(recipients) > 3:

            event_type = "bulk_email"

        elif external:

            event_type = "external_email"

        elif size > 50000:

            event_type = "large_internal_email"

        else:

            event_type = "internal_email"

        event = create_event(
            timestamp=row["date"],
            user=row["user"],
            event_type=event_type,
            metadata={
                "to": row.get("to"),
                "size": row.get("size")
            }
        )

        events.append(event)

    return events