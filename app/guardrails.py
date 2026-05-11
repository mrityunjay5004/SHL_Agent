

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
    "bank account"
]


# External competitors / non-SHL tools
NON_SHL_COMPETITORS = [
    "hackerrank",
    "codility",
    "testgorilla",
    "mettl",
    "criteria",
    "indeed assessment",
    "linkedin assessment"
]


def normalize_text(text: str) -> str:
    """
    Normalize user text for safer matching.
    """

    return text.lower().strip()


def contains_blocked_topic(text: str) -> bool:
    """
    Detect clearly off-topic or unsafe queries.
    """

    text = normalize_text(text)

    for topic in BLOCKED_TOPICS:

        if topic in text:
            return True

    return False


def contains_non_shl_request(text: str) -> bool:
    """
    Detect requests for non-SHL assessment platforms.
    """

    text = normalize_text(text)

    for company in NON_SHL_COMPETITORS:

        if company in text:
            return True

    return False


def detect_prompt_injection(text: str) -> bool:
    """
    Detect common prompt injection attempts.
    """

    text = normalize_text(text)

    injection_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "act as",
        "pretend to be",
        "system prompt",
        "developer message",
        "reveal instructions",
        "bypass rules",
        "jailbreak"
    ]

    for pattern in injection_patterns:

        if pattern in text:
            return True

    return False


def validate_user_input(text: str) -> Dict:
    """
    Main validation function used before orchestration.
    """

    if contains_blocked_topic(text):

        return {
            "allowed": False,
            "reason": (
                "I can only help with "
                "SHL assessment recommendations."
            )
        }

    if contains_non_shl_request(text):

        return {
            "allowed": False,
            "reason": (
                "I can only recommend "
                "assessments available in "
                "the SHL catalog."
            )
        }

    if detect_prompt_injection(text):

        return {
            "allowed": False,
            "reason": (
                "I can only assist with "
                "SHL assessment recommendations."
            )
        }

    return {
        "allowed": True,
        "reason": None
    }