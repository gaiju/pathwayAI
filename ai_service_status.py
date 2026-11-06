"""Safe messages for API failures; never display provider error bodies."""
import json
import logging
from urllib.error import URLError

BILLING_URL = "https://platform.openai.com/settings/organization/billing/overview"
# Log only fixed categories and allowlisted provider codes. Never log exception
# strings, URLs, headers, request/response bodies, prompts or account identifiers.
_LOGGER = logging.getLogger("pathwayai.ai_service")
_SAFE_CODES = frozenset({
    "insufficient_quota", "billing_hard_limit_reached", "billing_not_active",
    "rate_limit_exceeded", "invalid_api_key", "model_not_found",
    "permission_denied", "invalid_request_error", "invalid_value",
    "unsupported_parameter", "unsupported_value", "server_error",
    "service_unavailable", "context_length_exceeded",
})


def log_transport_error(error):
    category = "timeout" if isinstance(error, TimeoutError) else "connection_error" if isinstance(error, URLError) else "transport_error"
    _LOGGER.warning("PathwayAI AI failure: http_status=none error_code=%s", category)


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
    status = error.code if type(error.code) is int and 100 <= error.code <= 599 else "unknown"
    safe_code = next((detail.get(field) for field in ("code", "type")
                      if isinstance(detail.get(field), str) and detail[field] in _SAFE_CODES), "unrecognized")
    _LOGGER.warning("PathwayAI AI failure: http_status=%s error_code=%s", status, safe_code)
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
