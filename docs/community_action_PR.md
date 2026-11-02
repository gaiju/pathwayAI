## Problem and resulting behavior

Community Burden & Action has public evidence and planning tools, but lacks a concise connection between its evidence sources and audience-specific next steps. This adds “From Lyme Disease Burden to Community Action,” four practical nonclinical action areas, and three audience choices. The existing county brief includes the selected audience’s suggestions, source-backed HRSA resource context, and clearly separated small self-selected patient-survey context.

Existing tabs, county comparisons, calculations, optional inflation comparison, routes, personal records and multilingual defaults are retained. Missing resource values remain unavailable; no patient session data enters county reports. The existing PDF utility gains opt-in public-report footer and clickable source links, with unchanged patient defaults.

These are subsequent development changes, not claims about the originally submitted HHS MVP. No merge or deployment without owner approval.

## Validation

- Targeted community tests: 5 passed.
- Full branch suite: 99 tests, 96 passed, 3 pre-existing stale-label errors. Clean main baseline: 96 tests, 93 passed, the same 3 errors. See docs/community_action_review.md.
- Streamlit startup; desktop/mobile browser checks; audience and county selection; existing comparisons; PDF download; no page overflow or UI exceptions.
- 60 PDF combinations generated; 3–4 pages; 5 source links (6 with optional CPI); text page bounds and selected county/audience verified.
- Explicit missing-versus-zero handling, private-record exclusion, original cost arithmetic and survey limitations checked.

## Review assets

- docs/review/community_action_desktop.png
- docs/review/community_action_mobile.png
- docs/review/PathwayAI_Orange_Community_Action_Preview.pdf

## Limits

Surveillance remains 2024 NYSDOH, historical CDC context is 2019–2022, and HRSA resource fields are 2023. Newer releases are not freshly verified. The 33-person survey snapshot is small, self-selected and not representative of the selected county or U.S. population; raw responses and question-specific denominators remain unverified. Suggestions are not adopted services, clinical recommendations, or validated savings.
