from typing import List, Dict

def rerank(results: List[Dict], state: Dict) -> List[Dict]:
    """
    Reranks the retrieved assessments based on semantic similarity, state details,
    job levels, requested categories (personality, cognitive, simulation), and language support.
    """
    scored = []

    for item in results:
        # 1. Base Score (scaled from hybrid search similarity)
        score = item.get("hybrid_score", item.get("similarity_score", 0.0)) * 10.0

        name = item.get("name", "").lower()
        description = item.get("description", "").lower()
        keys = [k.lower() for k in item.get("keys", [])]
        job_levels = [lvl.lower() for lvl in item.get("job_levels", [])]
        languages = [lang.lower() for lang in item.get("languages", [])]

        # 2. Seniority Level Match (+5 points)
        if state.get("seniority"):
            seniority = state["seniority"]
            if seniority == "entry-level":
                if any(lvl in job_levels for lvl in ["entry-level", "graduate", "general population", "front line manager"]):
                    score += 5.0
            elif seniority == "mid-professional":
                if any(lvl in job_levels for lvl in ["mid-professional", "professional", "professional individual contributor"]):
                    score += 5.0
            elif seniority == "senior":
                if any(lvl in job_levels for lvl in ["senior", "lead", "professional individual contributor", "mid-professional"]):
                    score += 5.0
            elif seniority == "executive":
                if any(lvl in job_levels for lvl in ["executive", "director", "manager", "front line manager", "supervisor"]):
                    score += 5.0

        # 3. Preference Category Match / Penalty
        # Personality & Behavior
        is_personality_item = (
            any("personality" in k or "behavior" in k or "biodata" in k or "360" in k for k in keys)
            or any(kw in name for kw in ["opq", "dsi", "personality"])
        )
        if state.get("needs_personality") is True:
            if is_personality_item:
                score += 8.0
        elif state.get("needs_personality") is False:
            if is_personality_item:
                score -= 15.0  # Heavy penalty if explicitly negated

        # Cognitive / Ability
        is_cognitive_item = (
            any("ability" in k or "aptitude" in k for k in keys)
            or any(kw in name for kw in ["verify", "numerical", "reasoning", "cognitive", "statistics"])
        )
        if state.get("needs_cognitive") is True:
            if is_cognitive_item:
                score += 8.0
        elif state.get("needs_cognitive") is False:
            if is_cognitive_item:
                score -= 15.0

        # Simulation
        is_simulation_item = (
            any("simulation" in k or "exercise" in k or "situational" in k for k in keys)
            or any(kw in name for kw in ["simulation", "coding", "scenario", "interactive"])
        )
        if state.get("needs_simulation") is True:
            if is_simulation_item:
                score += 8.0
        elif state.get("needs_simulation") is False:
            if is_simulation_item:
                score -= 15.0

        # 4. Language Match (+10 points)
        if state.get("languages"):
            for requested_lang in state["languages"]:
                requested_lang_lower = requested_lang.lower()
                # Check if the requested accent or language is supported by the assessment
                if any(requested_lang_lower in lang for lang in languages):
                    score += 10.0
                elif requested_lang_lower == "us" and any("usa" in lang or "us" in lang for lang in languages):
                    score += 10.0

        # 5. Skills Overlap (+6 for name match, +3 for description match)
        if state.get("skills"):
            for skill in state["skills"]:
                skill_lower = skill.lower()
                if skill_lower in name:
                    score += 6.0
                if skill_lower in description:
                    score += 3.0

        # 6. Role Overlap (+4 points)
        if state.get("role"):
            role_lower = state["role"].lower()
            if role_lower in name:
                score += 4.0
            elif role_lower in description:
                score += 2.0

        # 7. Modern / New Version Boost
        if "(new)" in name:
            score += 2.0

        scored.append((score, item))

    # Sort items based on final score in descending order
    scored.sort(reverse=True, key=lambda x: x[0])

    return [x[1] for x in scored]