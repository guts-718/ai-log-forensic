from collections import Counter


# -----------------------------------
# CONTEXTUAL ENRICHMENT
# -----------------------------------
def enrich_sequence(sequence):

    enriched = []

    counts = Counter(sequence)

    for i, event in enumerate(sequence):

        tokens = []

        prev_event = None
        next_event = None

        if i > 0:
            prev_event = sequence[i - 1]

        if i < len(sequence) - 1:
            next_event = sequence[i + 1]

        # -----------------------------------
        # BASE EVENT
        # -----------------------------------
        tokens.append(event)

        # -----------------------------------
        # REPETITION
        # -----------------------------------
        if counts[event] >= 2:

            tokens.append(
                "repeated"
            )

        # -----------------------------------
        # EMAIL ENRICHMENT
        # -----------------------------------
        if "email" in event:

            tokens.append(
                "email_activity"
            )

            if "external" in event:

                tokens.append(
                    "external_comm"
                )

            if prev_event == "usb_insert":

                tokens.append(
                    "post_usb"
                )

            if prev_event == "mass_file_access":

                tokens.append(
                    "post_bulk_access"
                )

        # -----------------------------------
        # USB ENRICHMENT
        # -----------------------------------
        if "usb" in event:

            tokens.append(
                "usb_activity"
            )

            if next_event == "external_transfer":

                tokens.append(
                    "usb_exfil_chain"
                )

        # -----------------------------------
        # FILE ACCESS
        # -----------------------------------
        if "file_access" in event:

            tokens.append(
                "file_activity"
            )

            if "sensitive" in event:

                tokens.append(
                    "sensitive_access"
                )

            if next_event == "external_email":

                tokens.append(
                    "access_then_email"
                )

        # -----------------------------------
        # LOGON
        # -----------------------------------
        if "logon" in event:

            tokens.append(
                "auth_activity"
            )

            if "after_hours" in event:

                tokens.append(
                    "after_hours"
                )

        # -----------------------------------
        # EXFILTRATION
        # -----------------------------------
        if (
            event == "external_transfer"
        ):

            tokens.append(
                "data_exfiltration"
            )

            if prev_event == "usb_insert":

                tokens.append(
                    "staged_exfiltration"
                )

        # -----------------------------------
        # ARCHIVES
        # -----------------------------------
        if "archive" in event:

            tokens.append(
                "compression_activity"
            )

        # -----------------------------------
        # JOIN TOKEN
        # -----------------------------------
        if prev_event:
            tokens.append(
                "after_" + prev_event
            )
            
        final_token = "_".join(
            sorted(tokens)
        )

        enriched.append(
            final_token
        )

    return enriched