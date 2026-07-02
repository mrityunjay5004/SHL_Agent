import re
import json
from typing import Dict, List, Optional
from app.llm import generate_llm_response

# Seniority level normalized values
SENIORITY_MAPPING = {
    "cxo": "executive",
    "director": "executive",
    "vp": "executive",
    "executive": "executive",
    "president": "executive",
    "chief": "executive",
    "senior": "senior",
    "sr": "senior",
    "lead": "senior",
    "principal": "senior",
    "mid": "mid-professional",
    "middle": "mid-professional",
    "intermediate": "mid-professional",
    "mid-professional": "mid-professional",
    "professional individual contributor": "mid-professional",
    "entry": "entry-level",
    "graduate": "entry-level",
    "junior": "entry-level",
    "trainee": "entry-level",
    "associate": "entry-level",
    "intern": "entry-level",
    "beginner": "entry-level",
}

# Domain technical/non-technical skills in the catalogue
SKILLS_LIST = [
    "java", "python", "c++", "c#", "javascript", "typescript", "sql",
    "aws", "docker", "spring", "angular", "react", "linux", "networking",
    "hipaa", "excel", "word", "statistics", "accounting", "spoken english",
    "customer service", "sales", "finance"
]

def _extract_experience(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*\+?\s*(?:years|year|yrs|yr)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_state_rules(messages: List[Dict]) -> Dict:
    """
    Default deterministic rule-based state extraction from full conversation history.
    """
    state = {
        "role": None,
        "seniority": None,
        "experience": None,
        "skills": [],
        "hiring_purpose": None,
        "languages": [],
        "needs_personality": None,
        "needs_cognitive": None,
        "needs_simulation": None,
        "raw_query": ""
    }

    # Aggregate text for keyword checking, keeping sequence order
    user_msgs = [m["content"] for m in messages if m["role"] == "user"]
    full_text = " ".join(user_msgs).lower()
    state["raw_query"] = full_text

    # 1. Experience Check
    state["experience"] = _extract_experience(full_text)

    # 2. Seniority Check
    for kw, val in SENIORITY_MAPPING.items():
        # Match word boundaries to prevent substring matching
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, full_text):
            state["seniority"] = val
            break

    # 3. Skills Check
    extracted_skills = []
    for skill in SKILLS_LIST:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, full_text):
            extracted_skills.append(skill)
    state["skills"] = list(set(extracted_skills))

    # 4. Hiring Purpose Check
    if any(k in full_text for k in ["selection", "screen", "screening", "compare candidates", "hiring"]):
        state["hiring_purpose"] = "selection"
    elif any(k in full_text for k in ["development", "grow", "audit", "re-skill", "re-skilling", "restructuring"]):
        state["hiring_purpose"] = "development"

    # 5. Language Check
    if "spanish" in full_text:
        state["languages"].append("Spanish")
    if "english" in full_text:
        state["languages"].append("English")
    if "us" in full_text or "united states" in full_text:
        state["languages"].append("US")
    if "indian" in full_text:
        state["languages"].append("Indian")

    # 6. Preferences Check (tracking additions and drops over conversation history)
    # Loop user messages sequentially to allow corrections / refinements
    for msg in user_msgs:
        content = msg.lower()
        
        # Checking Negations / Drops
        is_negated_personality = any(k in content for k in ["remove opq", "drop opq", "without opq", "remove personality", "no personality", "drop personality"])
        is_negated_cognitive = any(k in content for k in ["remove cognitive", "drop cognitive", "no cognitive", "without cognitive"])
        is_negated_simulation = any(k in content for k in ["remove simulation", "drop simulation", "no simulation"])

        # Checking additions
        has_personality = any(k in content for k in ["personality", "behavior", "behaviour", "opq", "opq32r", "dsi"])
        has_cognitive = any(k in content for k in ["cognitive", "reasoning", "aptitude", "ability", "verify", "g+", "numerical"])
        has_simulation = any(k in content for k in ["simulation", "live coding", "coding", "programming", "scenarios"])

        if is_negated_personality:
            state["needs_personality"] = False
        elif has_personality:
            state["needs_personality"] = True

        if is_negated_cognitive:
            state["needs_cognitive"] = False
        elif has_cognitive:
            state["needs_cognitive"] = True

        if is_negated_simulation:
            state["needs_simulation"] = False
        elif has_simulation:
            state["needs_simulation"] = True

    # 7. Role Extraction (heuristic fallback)
    role_indicators = ["engineer", "developer", "manager", "analyst", "operator", "agent", "consultant"]
    for ind in role_indicators:
        pattern = r"\b([\w\-]+\s+" + ind + r")\b"
        match = re.search(pattern, full_text)
        if match:
            state["role"] = match.group(1)
            break
        elif ind in full_text:
            state["role"] = ind
            break

    return state

def extract_state_llm_fallback(messages: List[Dict], current_state: Dict) -> Dict:
    """
    LLM Fallback when rule-based extraction has low confidence or ambiguous context.
    """
    history_str = ""
    for m in messages:
        history_str += f"{m['role'].capitalize()}: {m['content']}\n"

    prompt = f"""
You are an expert recruitment state extractor for SHL assessments.
Given the conversation history and the current parsed state, return an updated and highly accurate state in JSON format.
Analyze the user's corrections, modifications, and exact details.

Conversation History:
{history_str}

Current State (pre-extracted by rules):
{json.dumps(current_state, indent=2)}

Return a JSON object conforming exactly to this schema:
{{
  "role": "job role title, or null if not mentioned",
  "seniority": "one of: 'entry-level', 'mid-professional', 'senior', 'executive', or null",
  "experience": "number of years (as integer or string), or null",
  "skills": ["list of technical/domain skills, e.g. ['Java', 'Spring']"],
  "hiring_purpose": "one of: 'selection', 'development', 'restructuring', 're-skilling', or null",
  "languages": ["list of requested assessment languages, e.g. ['Spanish', 'English (US)']"],
  "needs_personality": true/false/null,
  "needs_cognitive": true/false/null,
  "needs_simulation": true/false/null,
  "intent": "recommendation" | "comparison" | "refinement" | "clarification_response" | "confirmation" | "off_topic"
}}

Respond ONLY with valid JSON. Do not include markdown code block formatting (like ```json ... ```).
"""
    try:
        response_text = generate_llm_response(prompt)
        # Clean potential markdown output
        response_text = re.sub(r"^```json\s*", "", response_text, flags=re.IGNORECASE)
        response_text = re.sub(r"\s*```$", "", response_text, flags=re.IGNORECASE)
        
        extracted = json.loads(response_text)
        
        # Merge LLM results back into state
        for key in ["role", "seniority", "experience", "skills", "hiring_purpose", "languages", "needs_personality", "needs_cognitive", "needs_simulation", "intent"]:
            if key in extracted:
                current_state[key] = extracted[key]
                
    except Exception as e:
        # Fallback to rules if LLM fails
        current_state["intent"] = "recommendation"
        
    return current_state

def extract_state(messages: List[Dict]) -> Dict:
    """
    Main state extraction entrypoint. Evaluates rules first and falls back to LLM when confidence is low.
    """
    state = extract_state_rules(messages)
    latest_user = messages[-1]["content"].lower()

    # Trigger LLM Fallback only if:
    # 1. Rules extracted nothing useful and query is long/complex
    # 2. User specifies a complex correction/refinement (negation or drop words)
    # 3. User is asking a comparison query
    has_extracted = state["role"] is not None or state["seniority"] is not None or len(state["skills"]) > 0
    is_refinement = any(k in latest_user for k in ["instead", "change", "replace", "remove", "drop"])
    is_comparison = any(k in latest_user for k in ["difference", "compare", "vs", "versus"])

    needs_fallback = (
        (not has_extracted and len(latest_user.split()) > 8)
        or is_refinement
        or is_comparison
    )

    if needs_fallback:
        state = extract_state_llm_fallback(messages, state)
    else:
        # Default intent
        state["intent"] = "recommendation"

    return state