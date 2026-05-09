def pretty_print_path(G, path_data):
    path = path_data["path"]
    score = path_data["score"]

    separator = "=" * 70

    print(f"\n{separator}")
    print(f"🚨 SUSPICIOUS PATH DETECTED | Score: {score}")
    print(separator)

    # Template matches
    matches = path_data.get("template_matches", [])

    if matches:
        print("\n🎯 Attack Matches")
        print("-" * 70)

        for idx, match in enumerate(matches, start=1):
            print(
                f"[{idx}] {match['template']}\n"
                f"    ├─ Score       : {match['score']}\n"
                f"    └─ Completion  : {match['completion_ratio']}"
            )

    print("\n🛣️  Path Timeline")
    print("-" * 70)

    for idx, node in enumerate(path, start=1):
        node_data = G.nodes[node]

        if node_data.get("node_type") == "event":
            event_type = node_data.get("event_type", "UNKNOWN")
            timestamp = node_data.get("timestamp", "N/A")

            print(
                f"[{idx}] {node}\n"
                f"    ├─ Event Type : {event_type}\n"
                f"    └─ Timestamp  : {timestamp}"
            )

    print(f"{separator}\n")