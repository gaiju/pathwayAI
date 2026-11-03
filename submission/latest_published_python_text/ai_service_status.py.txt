"""Safe messages for API failures; never display provider error bodies."""
import json

BILLING_URL = "https://platform.openai.com/settings/organization/billing/overview"
LIMITS_URL = "https://platform.openai.com/settings/organization/limits"


def classify_api_error(error):
    """Distinguish exhausted quota from temporary 429 throttling."""
    try:
        body = json.loads(error.read(65536).decode("utf-8"))
        detail = body.get("error", {}) if isinstance(body, dict) else {}
        if not isinstance(detail, dict):
            detail = {}
    except (ValueError, UnicodeError, OSError):
        detail = {}
    exhausted = any(detail.get(field) in (
        "insufficient_quota", "billing_hard_limit_reached", "billing_not_active"
    ) for field in ("code", "type"))
    if exhausted:
        return {
            "kind": "quota",
            "message": "AI is temporarily unavailable because the service account's API quota or billing limit was reached. Other app features remain available.",
        }
    if error.code == 429:
        return {
            "kind": "rate_limit",
            "message": "The AI service is temporarily busy. Please try again later. Other app features remain available.",
        }
    return {
        "kind": "unavailable",
        "message": "The AI service is temporarily unavailable. Other app features remain available.",
    }
