import random
from datetime import datetime, timedelta


def generate_timestamp(base, minutes):
    return (base + timedelta(minutes=minutes)).isoformat()


def normal_user(user="U1"):
    base = datetime(2024, 1, 1, 10, 0)

    events = []
    for i in range(50):
        events.append({
            "timestamp": generate_timestamp(base, i * 5),
            "user": user,
            "event_type": random.choice(["logon", "file"])
        })

    return events


def file_to_usb_attack(user="U2"):
    base = datetime(2024, 1, 1, 11, 0)

    return [
        {"timestamp": generate_timestamp(base, 0), "user": user, "event_type": "logon"},
        {"timestamp": generate_timestamp(base, 5), "user": user, "event_type": "file"},
        {"timestamp": generate_timestamp(base, 6), "user": user, "event_type": "file"},
        {"timestamp": generate_timestamp(base, 7), "user": user, "event_type": "device"},
    ]


def email_exfiltration(user="U3"):
    base = datetime(2024, 1, 1, 12, 0)

    return [
        {"timestamp": generate_timestamp(base, 0), "user": user, "event_type": "file"},
        {"timestamp": generate_timestamp(base, 2), "user": user, "event_type": "email"},
        {"timestamp": generate_timestamp(base, 3), "user": user, "event_type": "email"},
    ]


def off_hours_login(user="U4"):
    base = datetime(2024, 1, 1, 2, 0)

    return [
        {"timestamp": generate_timestamp(base, 0), "user": user, "event_type": "logon"}
    ]


def multi_channel_attack(user="U5"):
    base = datetime(2024, 1, 1, 13, 0)

    return [
        {"timestamp": generate_timestamp(base, 0), "user": user, "event_type": "file"},
        {"timestamp": generate_timestamp(base, 2), "user": user, "event_type": "email"},
        {"timestamp": generate_timestamp(base, 3), "user": user, "event_type": "device"},
    ]


def generate_all():
    events = []
    events += normal_user()
    events += file_to_usb_attack()
    events += email_exfiltration()
    events += off_hours_login()
    events += multi_channel_attack()

    return events


if __name__ == "__main__":
    import json

    events = generate_all()

    with open("test_events.json", "w") as f:
        json.dump(events, f, indent=2)

    print("Generated test_events.json")