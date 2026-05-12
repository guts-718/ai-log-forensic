import pandas as pd

def normalize_events(events):
    for e in events:
        # Convert timestamp
        e["timestamp"] = pd.to_datetime(e["timestamp"])
    return events





# from collections import defaultdict


# # -----------------------------------
# # SENSITIVE FILE KEYWORDS
# # -----------------------------------
# # If a filename/resource contains
# # any of these keywords,
# # it may indicate access to
# # sensitive organizational data.
# SENSITIVE_KEYWORDS = [
#     "confidential",
#     "secret",
#     "salary",
#     "finance",
#     "payroll",
#     "internal",
#     "customer",
#     "employee"
# ]


# # -----------------------------------
# # ARCHIVE EXTENSIONS
# # -----------------------------------
# # File extensions commonly used
# # for compressed archives.
# #
# # Useful for detecting:
# # - bulk compression
# # - possible data exfiltration
# # - staging before transfer
# ARCHIVE_EXTENSIONS = [
#     ".zip",
#     ".rar",
#     ".7z",
#     ".tar"
# ]


# # -----------------------------------
# # MAP / ENRICH EVENTS
# # -----------------------------------
# #
# # Converts raw generic events into
# # semantically meaningful security events.
# #
# # Example:
# # "file" -> "sensitive_file_access"
# #
# # This improves:
# # - anomaly detection
# # - graph analysis
# # - attack template matching
# def enrich_events(events):

#     # -----------------------------------
#     # USER FILE ACCESS TRACKER
#     # -----------------------------------
#     #
#     # Tracks how many files each user
#     # has accessed.
#     #
#     # defaultdict(int):
#     # automatically initializes missing
#     # users with value 0.
#     user_file_counter = defaultdict(int)

#     # Store enriched events
#     enriched = []

#     # -----------------------------------
#     # PROCESS EACH EVENT
#     # -----------------------------------
#     for event in events:

#         # Create mutable copy
#         # so original event remains unchanged
#         e = dict(event)

#         # Original raw event type
#         #
#         # Example:
#         # "file"
#         # "logon"
#         # "email"
#         event_type = e.get("event_type")

#         # Normalize resource name
#         #
#         # str() prevents None errors
#         # lower() enables case-insensitive matching
#         resource = (
#             str(e.get("resource", ""))
#             .lower()
#         )

#         # Extract metadata dictionary
#         metadata = e.get("metadata", {})

#         # ===================================
#         # LOGON SEMANTICS
#         # ===================================
#         if event_type == "logon":

#             # Extract login activity
#             #
#             # Example:
#             # "Logon Success"
#             # "Logon Failure"
#             activity = str(
#                 metadata.get("activity", "")
#             ).lower()

#             # Failed login attempt
#             if "fail" in activity:

#                 e["event_type"] = (
#                     "failed_logon"
#                 )

#             # User logged out
#             elif "logoff" in activity:

#                 e["event_type"] = "logoff"

#             # Successful login
#             else:

#                 e["event_type"] = (
#                     "successful_logon"
#                 )

#         # ===================================
#         # FILE ACCESS SEMANTICS
#         # ===================================
#         elif event_type == "file":

#             # Identify current user
#             user = e.get("user")

#             # Increment file access counter
#             # for this user
#             user_file_counter[user] += 1

#             # Default semantic label
#             e["event_type"] = "file_access"

#             # -----------------------------------
#             # SENSITIVE FILE DETECTION
#             # -----------------------------------
#             #
#             # Example:
#             # payroll.xlsx
#             # confidential_report.pdf
#             #
#             # any():
#             # returns True if at least one
#             # keyword matches
#             if any(
#                 k in resource
#                 for k in SENSITIVE_KEYWORDS
#             ):

#                 e["event_type"] = (
#                     "sensitive_file_access"
#                 )

#             # -----------------------------------
#             # ARCHIVE CREATION DETECTION
#             # -----------------------------------
#             #
#             # Detect compressed files
#             # possibly created for transfer
#             if any(
#                 resource.endswith(ext)
#                 for ext in ARCHIVE_EXTENSIONS
#             ):

#                 e["event_type"] = (
#                     "archive_creation"
#                 )

#             # -----------------------------------
#             # BULK FILE ACCESS DETECTION
#             # -----------------------------------
#             #
#             # If user accesses many files,
#             # it may indicate suspicious activity.
#             #
#             # Threshold:
#             # > 20 accesses
#             if user_file_counter[user] > 20:

#                 e["event_type"] = (
#                     "bulk_file_access"
#                 )

#         # ===================================
#         # DEVICE SEMANTICS
#         # ===================================
#         elif event_type == "device":

#             # Extract device activity
#             activity = str(
#                 metadata.get("activity", "")
#             ).lower()

#             # Detect USB insertion/connect events
#             if (
#                 "connect" in activity
#                 or "insert" in activity
#             ):

#                 e["event_type"] = "usb_insert"

#             # Generic device activity
#             else:

#                 e["event_type"] = (
#                     "device_activity"
#                 )

#         # ===================================
#         # EMAIL SEMANTICS
#         # ===================================
#         elif event_type == "email":

#             # Extract receiver email address
#             to_addr = str(
#                 metadata.get("to", "")
#             ).lower()

#             # Default email activity
#             e["event_type"] = "email_sent"

#             # -----------------------------------
#             # EXTERNAL EMAIL DETECTION
#             # -----------------------------------
#             #
#             # Detect transfers to
#             # personal/public mail services.
#             #
#             # Useful for:
#             # insider threat detection
#             if (
#                 "gmail" in to_addr
#                 or "yahoo" in to_addr
#                 or "hotmail" in to_addr
#             ):

#                 e["event_type"] = (
#                     "external_transfer"
#                 )

#         # ===================================
#         # HTTP / WEB SEMANTICS
#         # ===================================
#         elif event_type == "http":

#             # Extract visited URL
#             url = str(
#                 metadata.get("url", "")
#             ).lower()

#             # -----------------------------------
#             # CLOUD STORAGE DETECTION
#             # -----------------------------------
#             #
#             # Detect uploads to cloud services
#             # commonly used for exfiltration.
#             if (
#                 "drive.google" in url
#                 or "dropbox" in url
#                 or "mega.nz" in url
#             ):

#                 e["event_type"] = (
#                     "cloud_upload"
#                 )

#             # Generic browsing activity
#             else:

#                 e["event_type"] = "web_activity"

#         # ===================================
#         # PROCESS EVENTS
#         # ===================================
#         elif event_type == "process":

#             # Extract process/application name
#             process_name = str(
#                 metadata.get("process", "")
#             ).lower()

#             # Default process activity
#             e["event_type"] = "process_start"

#             # -----------------------------------
#             # ENCRYPTION / RANSOMWARE DETECTION
#             # -----------------------------------
#             #
#             # Detect suspicious process names
#             # related to encryption/ransomware.
#             if (
#                 "encrypt" in process_name
#                 or "ransom" in process_name
#             ):

#                 e["event_type"] = (
#                     "encryption_activity"
#                 )

#         # Store enriched event
#         enriched.append(e)

#     # Return enriched semantic events
#     return enriched