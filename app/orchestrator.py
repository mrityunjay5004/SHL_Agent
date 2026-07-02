import re
import json
from typing import List, Dict, Tuple, Optional
from app.retriever import retrieve, lookup_by_name
from app.state_extractor import extract_state
from app.ranker import rerank
from app.guardrails import validate_user_input
from app.llm import generate_llm_response

def is_comparison_query(query: str) -> bool:
    query = query.lower()
    comparison_keywords = [
        "difference between",
        "compare",
        "vs",
        "versus",
        "difference"
    ]
    return any(keyword in query for keyword in comparison_keywords)

def extract_comparison_entities_llm(latest_user: str) -> List[str]:
    prompt = f"""
Identify the names of the two SHL assessments being compared in the user query.
User Query: "{latest_user}"

Respond with a JSON list containing exactly the two assessment names (e.g. ["DSI", "Safety & Dependability 8.0"]).
Respond ONLY with a valid JSON list.
"""
    try:
        response = generate_llm_response(prompt)
        response_text = re.sub(r"^```json\s*", "", response, flags=re.IGNORECASE)
        response_text = re.sub(r"\s*```$", "", response_text, flags=re.IGNORECASE)
        names = json.loads(response_text)
        if isinstance(names, list):
            return names
    except Exception:
        pass
    return []

def generate_comparison_reply(item1: Dict, item2: Dict, messages: List[Dict]) -> str:
    history_str = ""
    for m in messages[:-1]:
        history_str += f"{m['role'].capitalize()}: {m['content']}\n"
    history_str += f"User: {messages[-1]['content']}\n"

    prompt = f"""
Compare the following two SHL assessments using ONLY the provided catalog data.
Focus on their:
- purpose
- skills measured
- target audience
- duration
- assessment type (category)

Assessment 1: {json.dumps(item1, indent=2)}
Assessment 2: {json.dumps(item2, indent=2)}

Conversation History Context:
{history_str}

Write a professional, concise comparison response (1-2 paragraphs). Do not hallucinate or make assumptions not supported by the catalog data.
"""
    return generate_llm_response(prompt)

def generate_recommendation_reply(state: Dict, recommendations: List[Dict], messages: List[Dict]) -> str:
    history_str = ""
    for m in messages[:-1]:
        history_str += f"{m['role'].capitalize()}: {m['content']}\n"
    history_str += f"User: {messages[-1]['content']}\n"

    recs_json = json.dumps(recommendations, indent=2)

    prompt = f"""
You are a senior AI recruitment assistant recommending assessments from the SHL catalog.
Given the conversation history, the current extracted requirements, and the selected shortlist, write a professional and context-aware response introducing the recommended assessments.

Conversation History:
{history_str}

Selected Shortlist:
{recs_json}

Rules:
- Explain briefly why these assessments fit the candidate's profile.
- Do not mention or suggest any assessments that are not in the selected shortlist.
- Keep the reply concise and professional (2-4 sentences).
- Do not mention URLs or link markdown in the text reply.
"""
    return generate_llm_response(prompt)

def generate_clarification_reply(messages: List[Dict]) -> str:
    history_str = ""
    for m in messages:
        history_str += f"{m['role'].capitalize()}: {m['content']}\n"

    prompt = f"""
You are an SHL assessment recommendation assistant.
The user's request is too vague or lacks key details (such as the specific job role, seniority level, skills/traits to measure, or spoken language accent if relevant).
Write a polite, concise clarification question to ask the user for the missing details.

Conversation History:
{history_str}

Respond with only the clarification question (1 sentence).
"""
    return generate_llm_response(prompt)

def get_test_type_code(item: Dict) -> str:
    keys = [k.lower() for k in item.get("keys", [])]
    if not keys:
        return "K"
    primary = keys[0]
    if "knowledge" in primary or "skills" in primary:
        return "K"
    if "personality" in primary or "behavior" in primary or "behaviour" in primary:
        return "P"
    if "ability" in primary or "aptitude" in primary or "cognitive" in primary:
        return "C"
    if "simulation" in primary or "exercise" in primary or "situational" in primary or "biodata" in primary:
        return "S"
    return "K"

def generate_response(messages: List[Dict]) -> Dict:
    latest_user = messages[-1]["content"]

    # 1. Guardrails check
    validation = validate_user_input(latest_user)
    if not validation["allowed"]:
        return {
            "reply": validation["reason"],
            "recommendations": [],
            "end_of_conversation": False
        }

    # 2. State extraction & intent detection
    state = extract_state(messages)
    intent = state.get("intent", "recommendation")

    # 3. Handle off-topic intent
    if intent == "off_topic":
        return {
            "reply": "I can only help with SHL assessment recommendations.",
            "recommendations": [],
            "end_of_conversation": False
        }

    # 4. Handle comparison intent
    if intent == "comparison" or is_comparison_query(latest_user):
        entities = state.get("comparison_entities", [])
        if not entities:
            entities = extract_comparison_entities_llm(latest_user)
        
        if len(entities) >= 2:
            item1 = lookup_by_name(entities[0])
            item2 = lookup_by_name(entities[1])
            
            if item1 and item2:
                reply = generate_comparison_reply(item1, item2, messages)
                return {
                    "reply": reply,
                    "recommendations": [],
                    "end_of_conversation": False
                }
        
        return {
            "reply": "I could not find enough catalog information to compare those SHL assessments.",
            "recommendations": [],
            "end_of_conversation": False
        }

    # 5. Handle vague requests & clarification
    # Ask for clarification if key details (role/skills) are completely missing and no preferences are set
    is_vague = (
        not state.get("role")
        and not state.get("skills")
        and not state.get("needs_personality")
        and not state.get("needs_cognitive")
        and not state.get("needs_simulation")
    )
    # Check if a specific language is missing for contact center spoken screening
    is_svar_vague = (
        state.get("role") == "agent"
        and "spoken english" in state.get("skills", [])
        and not state.get("languages")
    )

    if is_vague or is_svar_vague or state.get("needs_clarification"):
        reply = generate_clarification_reply(messages)
        return {
            "reply": reply,
            "recommendations": [],
            "end_of_conversation": False
        }

    # 6. Semantic & hybrid retrieval
    search_query = f"{state.get('role') or ''} {' '.join(state.get('skills', []))} {state.get('seniority') or ''}"
    retrieved = retrieve(search_query, top_k=25)

    # 7. Reranking
    ranked = rerank(retrieved, state)

    # 8. Selection
    top_results = ranked[:5]
    
    recommendations = []
    for item in top_results:
        recommendations.append({
            "name": item["name"],
            "url": item["link"],
            "test_type": get_test_type_code(item)
        })

    # 9. Response generation
    end_of_conversation = state.get("end_of_conversation", False)
    
    # Check if user says closing confirmation
    if intent == "confirmation" or any(k in latest_user.lower() for k in ["perfect", "that works", "thanks", "thank you", "confirmed", "lock it in"]):
        end_of_conversation = True
        reply = "Shortlist confirmed. Glad I could help you shape the assessment battery! Let me know if you need anything else."
    else:
        reply = generate_recommendation_reply(state, recommendations, messages)

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": end_of_conversation
    }