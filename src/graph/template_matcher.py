from src.graph.attack_templates import ATTACK_TEMPLATES


# -----------------------------------
# CHECK EVENT MATCH
# -----------------------------------
def event_matches_stage(event_type, stage):

    return event_type in stage


# -----------------------------------
# MATCH TEMPLATE AGAINST PATH
# -----------------------------------
def match_template_to_path(
    G,
    path,
    template_name,
    template
):

    stages = template["stages"]

    stage_scores = template["stage_scores"]

    score = 0

    matched_stages = []

    stage_idx = 0

    # iterate path
    for node in path:

        node_data = G.nodes[node]

        if node_data.get("node_type") != "event":
            continue

        event_type = node_data.get("event_type")

        if stage_idx >= len(stages):
            break

        current_stage = stages[stage_idx]

        # stage matched
        if event_matches_stage(
            event_type,
            current_stage
        ):

            score += stage_scores[stage_idx]

            matched_stages.append(event_type)

            stage_idx += 1

    # transition bonus
    if stage_idx >= 2:
        score += template["transition_bonus"]

    # partial match handling
    completion_ratio = (
        stage_idx / len(stages)
    )

    score *= completion_ratio

    matched = (
    completion_ratio >= 0.4
    and score >= 5
    )

    return {
        "matched": matched,
        "template": template_name,
        "score": round(score, 2),
        "completion_ratio": round(completion_ratio, 2),
        "matched_stages": matched_stages
    }


# -----------------------------------
# MATCH ALL TEMPLATES
# -----------------------------------
def match_all_templates(
    G,
    path
):

    results = []

    for (
        template_name,
        template
    ) in ATTACK_TEMPLATES.items():

        result = match_template_to_path(
            G,
            path,
            template_name,
            template
        )

        if result["matched"]:
            results.append(result)

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results