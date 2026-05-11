from app.retriever import retrieve
from app.state_extractor import extract_state
from app.ranker import rerank
from app.guardrails import validate_user_input


def generate_response(messages):

    latest_user = messages[-1]["content"]

    # Guardrails
    validation = validate_user_input(
        latest_user
    )

    if not validation["allowed"]:

        return {
            "reply": validation["reason"],
            "recommendations": [],
            "end_of_conversation": False
        }

    # Clarification
    if len(latest_user.split()) < 4:

        return {
            "reply": (
                "Could you share the role, "
                "seniority level, and the "
                "skills or traits you want "
                "to assess?"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # Extract conversation state
    state = extract_state(messages)

    # Semantic retrieval
    retrieved = retrieve(latest_user)

    # Reranking
    ranked = rerank(retrieved, state)

    top_results = ranked[:5]

    recommendations = []

    for item in top_results:

        recommendations.append({
            "name": item["name"],
            "url": item["link"],
            "test_type": (
                item["keys"][0]
                if item.get("keys")
                else "Assessment"
            )
        })

    return {
        "reply": (
            "Here are some SHL assessments "
            "that align with your hiring needs."
        ),
        "recommendations": recommendations,
        "end_of_conversation": False
    }