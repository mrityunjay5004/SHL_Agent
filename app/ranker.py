def rerank(results, state):

    scored = []

    for item in results:

        score = 0

        description = item.get(
            "description",
            ""
        ).lower()

        keys = " ".join(
            item.get("keys", [])
        ).lower()

        name = item.get(
            "name",
            ""
        ).lower()

        # Skill matching
        for skill in state["skills"]:

            if skill in description:
                score += 4

            if skill in name:
                score += 4

        # Communication boost
        if (
            "communication" in state["skills"]
        ):

            if (
                "communication" in description
                or "communication" in keys
            ):

                score += 6

        # Personality boost
        if state["needs_personality"]:

            if (
                "personality" in keys
                or "behavior" in keys
            ):

                score += 8

        # Simulation boost
        if state["needs_simulation"]:

            if "simulation" in keys:

                score += 5

        # Cognitive boost
        if state["needs_cognitive"]:

            if (
                "ability" in keys
                or "aptitude" in keys
            ):

                score += 5

        scored.append((score, item))

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [x[1] for x in scored]