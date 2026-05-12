from .base_event import create_event

from src.enrichment.semantic_enricher import (
    enrich_event
)


def parse_file(df):

    events = []

    for _, row in df.iterrows():

        filename = str(
            row.get("filename", "")
        ).lower()

        if (
            "salary" in filename
            or "payroll" in filename
            or "finance" in filename
        ):

            event_type = (
                "sensitive_file_access"
            )

        elif (
            ".zip" in filename
            or ".rar" in filename
            or ".7z" in filename
        ):

            event_type = (
                "archive_creation"
            )

        else:

            event_type = (
                "normal_file_access"
            )

        event = create_event(
            timestamp=row["date"],
            user=row["user"],
            event_type=event_type,
            resource=row.get("filename"),
            metadata={
                "activity": row.get("activity")
            }
        )

        events.append(event)

    return events