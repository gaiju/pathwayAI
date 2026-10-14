# Final-day MVP improvements

## Changes

- The opening now leads with making invisible burden visible, its audience and
  practical outputs. The outdoor entry point remains broad and travel-friendly.
- Readers choose **Short and simple** (default) or **More detail** at the start.
  The shorter view uses familiar language and collapses longer learning/reference
  content. It is not a clinically validated cognitive-accessibility intervention.
- The community page demonstrates a fictional card → comparable summary →
  possible support response. Six authored cards are independent of real patient
  entries and production files. Unknown values stay unknown; small groups are
  withheld. No live reporting backend was added.
- Patient summaries include entered medical + other spending, while work-loss
  valuation stays separate. Input field keys and pilot schemas remain intact.
- Lyme testing education covers preparation, cost-estimate questions, overall
  results versus individual rows, and a downloadable checklist. No private
  patient report is published or sent to AI.
- Unverified diagnosis-delay survey comparisons moved out of headline results
  into the bottom archive. Numeric survey assertions were removed from the main
  community brief and public AI evidence bundle pending verification.
- Methods, status, source limitations, AI policy and longer privacy explanations
  appear at the bottom as small notes. Clinical safety and synthetic labels
  remain visible; the AI opt-in still explains external processing in its help.

## Feedback actually available

| Feedback reported in this conversation | Change or follow-up |
| --- | --- |
| Commissioner questioned purpose, audience, concrete benefit and distracting explanatory text | Clear value statement, usable support contacts, bottom methods/status |
| Outdoor ZIP 22180 returned Richmond rather than Fairfax | National boundaries and containment; user confirmed Fairfax in test app |
| Outdoor entry felt too narrowly framed around tick bites | "I want to plan a safer outdoor visit" |
| Literacy, vocabulary and cognitive load vary between users and days | Reading preference, plain labels and shorter default view |
| Test reports and prices are confusing | Public testing guide and preparation checklist |
| Network testers did not report a login requirement | Supports access availability; not a formal usability study |

These are reported stakeholder observations and technical checks, not proof of
health improvement, adoption, savings or representative user validation. No
clinical/county partnership or formal testing sample is claimed.

## Validation

Focused tests cover geography, evidence retrieval/citation IDs, fictional
aggregation, missing values, comparable periods/phases and synthetic exports.
All 14 focused tests passed. Streamlit rendering checks passed for the landing,
patient card, mode changes with entries/edits retained, both testing-guide views,
clinical safety, fictional summary/export and missing fields. The outdoor flow
passed with a mocked Vienna lookup returning Fairfax. Small captions appear only
in the bottom Notes and sources drawer; privacy remains in the AI opt-in help.
These are technical checks, not formal literacy, cognitive-accessibility or
clinical validation.

## Limits and release

Changes are staged on `rag-test`, not `main`. The original public submission app
may still use `main`; publication/deployment is a separate step. Live LLM behavior
and original source-table contents remain unverified in this environment. Public
collection remains off by default; secure production aggregation is unfinished.
The attached reports' suggested delay-to-savings engine, new diseases and FHIR
integration were intentionally deferred rather than presented as implemented.

## Follow-up: restore the preferred community workflow

The Community page again starts with the New York map and Dutchess/Orange
comparison (including language), then planning responses and cost breakdown.
The fictional cohort is no longer shown as the primary workflow. A private
session preview reuses earlier patient-entered costs, days lost and caregiver
hours without repeat entry; it is not shared evidence. Input snapshots and the
story remain in the current private session and are removed by Clear session.
Shared collection and consent rules are unchanged. A navigation check confirmed
the map-first layout, reuse of entered values, and restoration when returning
to Care & Support.

## Optional tick observations

The same record now includes when a tick was found (exact or approximate), where
it was found (ZIP or county/state), and current care location. Locations remain
separate from county of residence. Existing story locations are used as initial
suggestions where available; entered details survive page changes and are reused
in the personal download and private community preview. Current care location
also generates a care-search link without requiring another location entry.
Observations are labeled patient-reported and unverified. No new shared storage
or surveillance case count was created; production tick reporting still requires
reviewed consent and a secure pilot.

## Navigation and vocabulary check

All four main routes and their Back to start controls passed rendering/navigation
checks. Both cost-exploration buttons open their intended pages. OOP abbreviations
in app displays/downloads are expanded to out-of-pocket, with a definition in
the personal form and published-reference panels: money the person paid, not
insurer payments. Existing records are reused; references do not predict bills.
