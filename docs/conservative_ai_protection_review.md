# Conservative API protection review

Review branch: `fix/conservative-ai-protection`, based on published `aaecdc4`. Not merged or deployed. This replaces the broader reliability proposal in response to the owner's clarification.

## Approved implementation scope

- Keep `_ai_bucket` unchanged: the existing keyed per-connection limit remains, including the shared unknown-connection bucket. Do not add a per-session fallback.
- Preserve three requests per connection/30 minutes and five requests per session, pre-request reservations, consent and no automatic retries.
- Add an atomic shared ceiling of 60 requests/hour per app server, configurable using positive `PATHWAYAI_AI_SERVER_MAX_REQUESTS`. The longer cleanup window keeps both the 30-minute connection window and one-hour server window accurate. No configuration change is required for the default.
- Keep safe public errors with allowlisted diagnostic categories across the existing English extraction, text and live public-evidence helpers. Preserve fixed internal quota notices; do not log notes, keys, bodies, URLs or arbitrary exception text.
- Hide the decorative section-hero icon group from assistive technology; preserve meaningful labels and image alternatives.

## Explicitly excluded

No image compression, image relocation, map relocation or session-fallback loosening. Tests compare all embedded photo strings and the connection-bucket function with the published baseline exactly. The large homepage image is unchanged. No patient-history draft, county-report draft, Blue Button or FHIR work is included.

## Limits

The shared unknown-connection bucket can still restrict different visitors when the host does not provide a usable address. This is intentionally retained to prioritize conservative API protection.

The local SQLite ceiling applies to one app server. It is not a guaranteed dollar-spending cap, a multi-server global limit, or protection against direct use of a stolen API key. Token usage varies; local storage/restarts and multiple instances affect enforcement. Existing private key storage, provider account monitoring and appropriate provider controls remain necessary. No claim is made that malicious use is impossible.

## Validation

Five focused tests passed: unchanged connection policy/photos, independent expiry windows, concurrent shared-limit enforcement, no outbound API request after session/service blocking, and safe errors across existing AI routes. No real patient data or live/billable API requests were used. The full regression results are recorded below when complete.

Final result: **142 regression tests passed in 169.803 seconds**, including the five new protection tests. `git diff --check` passed. Existing Streamlit deprecation/fontconfig warnings remained non-fatal. No image asset, map dataset, public API request or production deployment was changed by this review work.
