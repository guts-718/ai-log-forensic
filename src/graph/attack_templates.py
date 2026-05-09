# -----------------------------
# ATTACK TEMPLATES
# -----------------------------

ATTACK_TEMPLATES = {

    # -----------------------------------
    # DATA EXFILTRATION
    # -----------------------------------
    "data_exfiltration": {
        "stages": [

            ["logon"],

            [
                "file_access",
                "sensitive_file_access"
            ],

            [
                "usb_insert",
                "device_connect"
            ],

            [
                "compression",
                "archive_creation"
            ],

            [
                "email_sent",
                "external_transfer"
            ]
        ],

        "stage_scores": [
            1,
            3,
            5,
            4,
            6
        ],

        "transition_bonus": 5,

        "time_bonus": 3,

        "min_score": 10
    },

    # -----------------------------------
    # RANSOMWARE
    # -----------------------------------
    "ransomware": {
        "stages": [

            ["process_start"],

            [
                "privilege_escalation",
                "admin_activity"
            ],

            [
                "mass_file_modification",
                "bulk_file_access"
            ],

            [
                "encryption_activity"
            ],

            [
                "backup_deletion"
            ]
        ],

        "stage_scores": [
            2,
            5,
            6,
            8,
            7
        ],

        "transition_bonus": 6,

        "time_bonus": 4,

        "min_score": 15
    },

    # -----------------------------------
    # BRUTE FORCE
    # -----------------------------------
    "brute_force": {
        "stages": [

            [
                "failed_logon"
            ],

            [
                "failed_logon"
            ],

            [
                "failed_logon"
            ],

            [
                "logon",
                "successful_logon"
            ]
        ],

        "stage_scores": [
            2,
            2,
            2,
            6
        ],

        "transition_bonus": 5,

        "time_bonus": 4,

        "min_score": 10
    },

    # -----------------------------------
    # LATERAL MOVEMENT
    # -----------------------------------
    "lateral_movement": {
        "stages": [

            [
                "logon"
            ],

            [
                "credential_access"
            ],

            [
                "remote_connection",
                "network_access"
            ],

            [
                "admin_activity",
                "privilege_escalation"
            ]
        ],

        "stage_scores": [
            2,
            5,
            6,
            7
        ],

        "transition_bonus": 6,

        "time_bonus": 3,

        "min_score": 12
    },

    # -----------------------------------
    # PRIVILEGE ESCALATION
    # -----------------------------------
    "privilege_escalation": {
        "stages": [

            [
                "failed_logon"
            ],

            [
                "successful_logon",
                "logon"
            ],

            [
                "admin_activity"
            ],

            [
                "privilege_escalation"
            ]
        ],

        "stage_scores": [
            2,
            4,
            6,
            8
        ],

        "transition_bonus": 5,

        "time_bonus": 3,

        "min_score": 12
    },

    # -----------------------------------
    # INSIDER THREAT
    # -----------------------------------
    "insider_threat": {
        "stages": [

            [
                "logon"
            ],

            [
                "sensitive_file_access",
                "bulk_file_access"
            ],

            [
                "usb_insert",
                "external_transfer",
                "email_sent"
            ]
        ],

        "stage_scores": [
            1,
            5,
            7
        ],

        "transition_bonus": 6,

        "time_bonus": 3,

        "min_score": 10
    },

    # -----------------------------------
    # DEVICE ABUSE
    # -----------------------------------
    "device_abuse": {
        "stages": [

            [
                "device_connect",
                "usb_insert"
            ],

            [
                "bulk_file_access"
            ],

            [
                "external_transfer"
            ]
        ],

        "stage_scores": [
            3,
            5,
            6
        ],

        "transition_bonus": 4,

        "time_bonus": 2,

        "min_score": 10
    },

    # -----------------------------------
    # ACCOUNT TAKEOVER
    # -----------------------------------
    "account_takeover": {
        "stages": [

            [
                "failed_logon"
            ],

            [
                "successful_logon"
            ],

            [
                "remote_connection"
            ],

            [
                "credential_access"
            ]
        ],

        "stage_scores": [
            3,
            5,
            6,
            7
        ],

        "transition_bonus": 5,

        "time_bonus": 3,

        "min_score": 12
    }
}