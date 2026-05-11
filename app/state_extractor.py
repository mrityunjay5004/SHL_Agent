def extract_state(messages):

    full_text = " ".join(
        [m["content"] for m in messages]
    ).lower()

    state = {
        "role": None,
        "seniority": None,
        "skills": [],
        "needs_personality": False,
        "needs_cognitive": False,
        "needs_simulation": False
    }

    seniority_keywords = {
        "entry": "entry-level",
        "junior": "junior",
        "mid": "mid-professional",
        "senior": "senior",
        "manager": "manager",
        "lead": "leadership",
        "director": "director"
    }

    for key, value in seniority_keywords.items():

        if key in full_text:
            state["seniority"] = value

    tracked_skills = [
        "java",
        "python",
        "sql",
        "aws",
        "backend",
        "frontend",
        "communication",
        "leadership",
        "analytics",
        "machine learning",
        "cloud",
        "developer"
    ]

    for skill in tracked_skills:

        if skill in full_text:
            state["skills"].append(skill)

    # Personality detection
    personality_terms = [
        "personality",
        "behavior",
        "culture fit",
        "leadership"
    ]

    for term in personality_terms:

        if term in full_text:
            state["needs_personality"] = True

    # Simulation detection
    simulation_terms = [
        "developer",
        "coding",
        "programming",
        "backend",
        "frontend"
    ]

    for term in simulation_terms:

        if term in full_text:
            state["needs_simulation"] = True

    # Cognitive detection
    cognitive_terms = [
        "aptitude",
        "cognitive",
        "problem solving"
    ]

    for term in cognitive_terms:

        if term in full_text:
            state["needs_cognitive"] = True

    return state