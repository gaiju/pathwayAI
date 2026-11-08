# Reliability, asset and accessibility review

Review branch: `fix/reliability-accessibility`; baseline published `aaecdc4`. Not merged or deployed. The unpublished patient-history branch is not included.

## Four focused changes

1. **AI limits.** Known connection addresses keep the existing keyed per-connection bucket. Missing/invalid addresses receive a stable, random per-session fallback, avoiding one shared unknown-address bucket. Preserve three requests per 30 minutes and five per session. Add an atomic, shared SQLite ceiling of 60 requests per hour per app server, configurable with positive `PATHWAYAI_AI_SERVER_MAX_REQUESTS`. Count reservations before outbound requests and retain no-auto-retry behavior. Keep one hour of timestamps so bucket and server windows work independently. Privacy wording now covers keyed session identifiers as well as connection identifiers.
2. **Public failures.** Replace raw exception/body text in English story extraction, the text-request helper and live public-evidence research with fixed user messages and allowlisted diagnostic categories. Preserve internally generated limit/quota notices. Remove exception interpolation from the combined map warning. Never log notes, request/response bodies, keys, URLs or arbitrary exception strings.
3. **Visual assets.** Extract four existing embedded photographs into `assets/page_photos/`, resize to at most 1200 px wide and JPEG-compress. Keep the same photos/aspect ratios and explicit alternative text. Render one image element, removing the repeated inline CSS background reference. Move the existing NY map geometry into `data/ny_county_map_boundaries.geojson`, using a cached local loader. Tests compare parsed geometry with the baseline exactly; no geography, source vintage or surveillance numbers change. The homepage forest asset remains unchanged.
4. **Decorative icons.** Mark the decorative section-hero icon group `aria-hidden=true`, retaining title text and meaningful image alternatives. This is a targeted fix, not a complete screen-reader audit.

`app.py` decreased from 2,485,736 to approximately 436,000 bytes (82.5%). The four image assets total 562,635 bytes versus approximately 1.49 MB of original image data. These are file-size measurements, not measured real-user loading-speed improvements.

## Files

`app.py`, `ai_service_status.py`, new `visual_assets.py`, four JPEG assets, moved map geometry, focused tests and review documentation/screenshots. No new dependencies, clinical content, patient storage or county-cost changes.

## Validation

Six focused tests passed, covering stable separate fallback buckets, known-address behavior, independent time windows/expiry, concurrent server-ceiling enforcement, safe errors/logs across existing AI routes, photo loading/alt text and identical map geometry. Existing seven AI status tests passed. Chromium checks passed desktop 1440 px and mobile 390 px: homepage/prevention navigation, image dimensions/alternative text, single photo element, no UI exceptions or horizontal document overflow. No live/billable AI requests or real patient data used. See final regression results below.

## Limits and next checks

- No evidence yet that the live host actually groups all visitors into an unknown bucket. A controlled two-network check after approved deployment can assess this.
- A valid shared IP can still share the connection limit, including a household/organization network, by design.
- Session fallback can be reset by new sessions. The server-wide ceiling helps limit this but is not an identity or fraud-prevention system.
- The local SQLite ceiling is **not** a multi-server global ceiling or a guaranteed dollar-spending cap. Restarts/redeployments/local persistence and token usage affect limits and cost; monitoring and appropriate provider controls remain necessary.
- Photos are recompressed, not byte-identical. Browser checks establish loading/layout, not universal perceptual equivalence or all-device speed gains.
- Existing Streamlit deprecation/fontconfig warnings are unrelated and not addressed here. Full assistive-technology testing remains outstanding.

No Blue Button, FHIR, disease expansion, broad module refactor or patient-history draft was included. These are subsequent improvements, not changes claimed as part of the original HHS submission.

## Final result

**143 regression tests passed in 160.246 seconds.** The first run identified one legacy test that expected inline base64 assets; it was updated to validate the migrated JPEGs, aspect ratios and display data, then the full suite passed. Six focused reliability tests and seven existing AI status tests also passed separately. Chromium desktop/mobile checks passed. `git diff --check` passed. Existing Streamlit deprecation and fontconfig cache warnings were non-fatal. These are technical checks, not clinical validation, live hosting verification or proof of faster user task completion.
