from collections import defaultdict


# -----------------------------------
# SENSITIVE FILE KEYWORDS
# -----------------------------------
SENSITIVE_KEYWORDS = [
    "confidential",
    "secret",
    "salary",
    "finance",
    "payroll",
    "internal",
    "customer",
    "employee"
]


# -----------------------------------
# ARCHIVE EXTENSIONS
# -----------------------------------
ARCHIVE_EXTENSIONS = [
    ".zip",
    ".rar",
    ".7z",
    ".tar"
]


# -----------------------------------
# MAP EVENT
# -----------------------------------
def enrich_events(events):

    # user activity tracking
    user_file_counter = defaultdict(int)

    enriched = []

    for event in events:

        e = dict(event)

        event_type = e.get("event_type")

        resource = (
            str(e.get("resource", ""))
            .lower()
        )

        metadata = e.get("metadata", {})

        # -----------------------------------
        # LOGON SEMANTICS
        # -----------------------------------
        if event_type == "logon":

            activity = str(
                metadata.get("activity", "")
            ).lower()

            if "fail" in activity:
                e["event_type"] = "failed_logon"

            elif "logoff" in activity:
                e["event_type"] = "logoff"

            else:
                e["event_type"] = "successful_logon"

        # -----------------------------------
        # FILE ACCESS SEMANTICS
        # -----------------------------------
        elif event_type == "file":

            user = e.get("user")

            user_file_counter[user] += 1

            e["event_type"] = "file_access"

            # sensitive file
            if any(
                k in resource
                for k in SENSITIVE_KEYWORDS
            ):

                e["event_type"] = (
                    "sensitive_file_access"
                )

            # archive creation
            if any(
                resource.endswith(ext)
                for ext in ARCHIVE_EXTENSIONS
            ):

                e["event_type"] = (
                    "archive_creation"
                )

            # bulk access
            if user_file_counter[user] > 20:

                e["event_type"] = (
                    "bulk_file_access"
                )

        # -----------------------------------
        # DEVICE SEMANTICS
        # -----------------------------------
        elif event_type == "device":

            activity = str(
                metadata.get("activity", "")
            ).lower()

            if (
                "connect" in activity
                or "insert" in activity
            ):

                e["event_type"] = "usb_insert"

            else:
                e["event_type"] = "device_activity"

        # -----------------------------------
        # EMAIL SEMANTICS
        # -----------------------------------
        elif event_type == "email":

            to_addr = str(
                metadata.get("to", "")
            ).lower()

            e["event_type"] = "email_sent"

            if (
                "gmail" in to_addr
                or "yahoo" in to_addr
                or "hotmail" in to_addr
            ):

                e["event_type"] = (
                    "external_transfer"
                )

        # -----------------------------------
        # HTTP / WEB
        # -----------------------------------
        elif event_type == "http":

            url = str(
                metadata.get("url", "")
            ).lower()

            if (
                "drive.google" in url
                or "dropbox" in url
                or "mega.nz" in url
            ):

                e["event_type"] = (
                    "cloud_upload"
                )

            else:
                e["event_type"] = "web_activity"

        # -----------------------------------
        # PROCESS EVENTS
        # -----------------------------------
        elif event_type == "process":

            process_name = str(
                metadata.get("process", "")
            ).lower()

            e["event_type"] = "process_start"

            if (
                "encrypt" in process_name
                or "ransom" in process_name
            ):

                e["event_type"] = (
                    "encryption_activity"
                )

        enriched.append(e)

    return enriched