

from typing import Dict


import re
from typing import Dict

# Topics outside SHL assessment recommendation scope
BLOCKED_TOPICS = [
    "salary",
    "compensation",
    "politics",
    "religion",
    "legal advice",
    "medical advice",
    "hack",
    "malware",
    "bypass",
    "jailbreak",
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "reveal prompt",
    "confidential data",
    "password",
    "social security",
    "bank account",
    "how much do they get paid",
    "compliance requirements under hipaa",
    "legally required"
]

# External competitors / non-SHL tools
NON_SHL_COMPETITORS = [
    "hackerrank",
    "codility",
    "testgorilla",
    "mettl",
    "criteria",
    "indeed assessment",
    "linkedin assessment",
    "coderpad",
    "glider",
    "triplebyte",
    "hirevue",
    "leetcode"
]

# Common prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(?:previous|all)\s+instructions",
    r"system\s+prompt",
    r"developer\s+message",
    r"reveal\s+instructions",
    r"bypass\s+rules",
    r"jailbreak",
    r"you\s+must\s+now\s+act",
    r"pretend\s+to\s+be",
    r"dan\s+mode",
    r"forget\s+everything",
    r"what\s+are\s+your\s+instructions",
    r"output\s+the\s+above"
]

def normalize_text(text: str) -> str:
    """
    Normalize user text for safer matching.
    """
    if not text:
        return ""
    text = text.lower().strip()
    # Remove basic punctuation to make comparisons cleaner
    text = re.sub(r"[^\w\s\-\+]", "", text)
    return text

def contains_blocked_topic(text: str) -> bool:
    """
    Detect clearly off-topic or unsafe queries.
    """
    normalized = normalize_text(text)
    
    # Check for direct phrase matches
    for topic in BLOCKED_TOPICS:
        if topic in normalized:
            return True
            
    # Also check if user is asking for general recruitment consulting unrelated to SHL
    if "hiring advice" in normalized or "how to interview" in normalized:
        return True
        
    return False

def contains_non_shl_request(text: str) -> bool:
    """
    Detect requests for non-SHL assessment platforms.
    """
    normalized = normalize_text(text)
    for company in NON_SHL_COMPETITORS:
        # Match as whole word boundary to prevent matching substrings of other words
        pattern = r"\b" + re.escape(company) + r"\b"
        if re.search(pattern, normalized):
            return True
    return False

def detect_prompt_injection(text: str) -> bool:
    """
    Detect common prompt injection attempts.
    """
    normalized = text.lower().strip()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized):
            return True
            
    return False

def validate_user_input(text: str) -> Dict:
    """
    Main validation function used before orchestration.
    """
    if detect_prompt_injection(text):
        return {
            "allowed": False,
            "reason": "I can only assist with SHL assessment recommendations."
        }

    if contains_blocked_topic(text):
        return {
            "allowed": False,
            "reason": "I can only help with SHL assessment recommendations."
        }

    if contains_non_shl_request(text):
        return {
            "allowed": False,
            "reason": "I can only recommend assessments available in the SHL catalog."
        }

    return {
        "allowed": True,
        "reason": None
    }