from datetime import datetime


# -----------------------------------
# HELPERS
# -----------------------------------
def is_after_hours(ts):

    if not ts:
        return False

    hour = ts.hour

    return hour < 6 or hour > 20


# -----------------------------------
# SEMANTIC ENRICHMENT
# -----------------------------------
def enrich_event(event):
    print(
    "ENRICH CALLED:",
    event.get("event_type")
)

    enriched = dict(event)

    event_type = event.get(
        "event_type",
        ""
    )

    metadata = event.get(
        "metadata",
        {}
    )

    timestamp = event.get(
        "timestamp"
    )

    resource = event.get(
        "resource"
    )

    # -----------------------------------
    # LOGON EVENTS
    # -----------------------------------
    if event_type == "successful_logon":

        if is_after_hours(timestamp):

            enriched["event_type"] = (
                "after_hours_logon"
            )

        else:

            enriched["event_type"] = (
                "normal_logon"
            )

    # -----------------------------------
    # EMAIL EVENTS
    # -----------------------------------
    elif event_type == "email_sent":

        recipients = str(
            metadata.get("to", "")
        ).split(";")

        size = metadata.get(
            "size",
            0
        )

        external = any(

            "@dtaa.com" not in r

            for r in recipients
        )

        if len(recipients) > 3:

            enriched["event_type"] = (
                "bulk_email"
            )

        elif external:

            enriched["event_type"] = (
                "external_email"
            )

        elif size > 50000:

            enriched["event_type"] = (
                "large_internal_email"
            )

        else:

            enriched["event_type"] = (
                "internal_email"
            )

    # -----------------------------------
    # USB EVENTS
    # -----------------------------------
    elif event_type == "usb_insert":

        size = metadata.get(
            "transfer_size_mb",
            0
        )

        if size > 500:

            enriched["event_type"] = (
                "large_usb_transfer"
            )

        elif is_after_hours(timestamp):

            enriched["event_type"] = (
                "after_hours_usb"
            )

        else:

            enriched["event_type"] = (
                "usb_insert"
            )

    # -----------------------------------
    # FILE ACCESS
    # -----------------------------------
    elif event_type == "bulk_file_access":

        count = metadata.get(
            "file_count",
            0
        )

        if count > 100:

            enriched["event_type"] = (
                "mass_file_access"
            )

        elif is_after_hours(timestamp):

            enriched["event_type"] = (
                "after_hours_file_access"
            )

        else:

            enriched["event_type"] = (
                "bulk_file_access"
            )

    # -----------------------------------
    # EXTERNAL TRANSFER
    # -----------------------------------
    elif event_type == "external_transfer":

        domain = metadata.get(
            "domain",
            ""
        )

        if "dropbox" in domain:

            enriched["event_type"] = (
                "cloud_exfiltration"
            )

        elif "drive.google" in domain:

            enriched["event_type"] = (
                "cloud_exfiltration"
            )

        else:

            enriched["event_type"] = (
                "external_transfer"
            )

    # -----------------------------------
    # ARCHIVE
    # -----------------------------------
    elif event_type == "archive_creation":

        enriched["event_type"] = (
            "compressed_archive_creation"
        )

    # -----------------------------------
    # FILE ACCESS
    # -----------------------------------
    elif event_type == "file_access":

        if resource:

            resource = str(resource).lower()

            if (
                "salary" in resource
                or "finance" in resource
                or "payroll" in resource
            ):

                enriched["event_type"] = (
                    "sensitive_file_access"
                )

            else:

                enriched["event_type"] = (
                    "normal_file_access"
                )

    return enriched