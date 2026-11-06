# Safe AI failure diagnostics

Review branch: `fix/safe-ai-diagnostics`. Prepared November 6, 2026. Not merged or deployed. This change is independent of the pending multilingual/county-report branch.

## Problem and change

The existing API wrapper catches HTTP failures and shows a safe public message, but it does not record a diagnostic status. Billing, authentication, model-access and service failures can therefore be difficult to distinguish from the live interface.

- Record one warning per failed outbound API request with a validated HTTP status and an allowlisted error code.
- Record a fixed category for connection errors/timeouts without HTTP status.
- Unknown provider codes become `unrecognized`; malformed bodies retain the existing generic user notice.
- Do not log request/response bodies, exception strings, notes, keys, headers, URLs, IP addresses or account identifiers.
- Preserve public notices, consent, request limits, billing behavior, request payloads and the no-automatic-retry policy.
- Refresh an older cached status helper on Streamlit rerun so the new logging function is available.

Example log line:

```
PathwayAI AI failure: http_status=401 error_code=invalid_api_key
```

This identifies an authentication failure; it does not reveal the key. `429` with `insufficient_quota` points to quota/billing; `429` with `rate_limit_exceeded` points to throttling. `model_not_found` may mean an incorrect model name or unavailable model access. `unrecognized` intentionally omits untrusted details and may require further investigation.

## Files

- `ai_service_status.py`: bounded parsing and safe diagnostics.
- `app.py`: helper refresh and transport logging in the existing request wrapper.
- `tests/test_ai_service_status.py`: existing classification tests plus sensitive-data exclusion, malformed/untrusted codes, transport logging and wrapper integration checks.

## Validation

Seven focused tests pass. Integration tests mock the network; no billable OpenAI requests and no real patient data are used. They verify one outbound attempt per call and preserve request counting. Full regression results are recorded below when complete.

## After approval to deploy

Open the live owner's Streamlit logs and trigger the failing workflow once using fictional notes. Find the newest `PathwayAI AI failure` line and use its status/code to investigate the configured API account/model. Failed requests count toward the existing app limits; do not repeatedly retry. This change does not fix or identify the current live failure until it is deployed and that failure occurs again. It does not change third-party or platform logging policies.

Final validation: **126 regression tests passed in 145.951 seconds**, including the seven focused diagnostic tests. `git diff --check` passed. Existing Streamlit deprecation warnings remain unrelated to this change. GitHub GraphQL returned Forbidden when creating a PR; the branch is pushed for review at https://github.com/gaiju/pathwayAI/compare/main...fix/safe-ai-diagnostics. No live API call, merge or deployment was performed.
