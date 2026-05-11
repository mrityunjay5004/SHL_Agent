import re

from app.retriever import retrieve
from app.state_extractor import extract_state
from app.ranker import rerank
from app.guardrails import validate_user_input


def is_comparison_query(query):

    query = query.lower()

    comparison_keywords = [
        "difference between",
        "compare",
        "vs",
        "versus",
        "difference"
    ]

    return any(
        keyword in query
        for keyword in comparison_keywords
    )


def extract_comparison_entities(query):

    query = query.lower()

    query = query.replace(
        "vs",
        "versus"
    )

    patterns = [

        r"difference between (.*?) and (.*)",

        r"compare (.*?) and (.*)",

        r"compare (.*?) versus (.*)",

        r"(.*?) versus (.*)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query
        )

        if match:

            entity1 = (
                match.group(1)
                .strip()
            )

            entity2 = (
                match.group(2)
                .strip()
            )

            return entity1, entity2

    return None, None


def build_comparison_response(
    entity1_data,
    entity2_data
):

    if not entity1_data or not entity2_data:

        return {
            "reply": (
                "I could not find enough "
                "catalog information to "
                "compare those SHL "
                "assessments."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    entity1_name = entity1_data["name"]

    entity2_name = entity2_data["name"]

    entity1_desc = (
        entity1_data.get(
            "description",
            ""
        )
    )

    entity2_desc = (
        entity2_data.get(
            "description",
            ""
        )
    )

    entity1_type = ", ".join(
        entity1_data.get(
            "keys",
            []
        )
    )

    entity2_type = ", ".join(
        entity2_data.get(
            "keys",
            []
        )
    )

    reply = f"""
{entity1_name} focuses on:

{entity1_desc}

Primary assessment areas:
{entity1_type}


{entity2_name} focuses on:

{entity2_desc}

Primary assessment areas:
{entity2_type}


Overall, {entity1_name} and
{entity2_name} differ in their
assessment focus, competencies,
and intended evaluation areas.
"""

    return {
        "reply": reply.strip(),
        "recommendations": [],
        "end_of_conversation": False
    }


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

    # Comparison handling
    if is_comparison_query(
        latest_user
    ):

        entity1, entity2 = (
            extract_comparison_entities(
                latest_user
            )
        )

        if entity1 and entity2:

            entity1_results = retrieve(
                entity1
            )

            entity2_results = retrieve(
                entity2
            )

            entity1_data = (
                entity1_results[0]
                if entity1_results
                else None
            )

            entity2_data = (
                entity2_results[0]
                if entity2_results
                else None
            )

            return (
                build_comparison_response(
                    entity1_data,
                    entity2_data
                )
            )

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
    ranked = rerank(
        retrieved,
        state
    )

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