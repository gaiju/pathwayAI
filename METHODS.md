# Methods and data dictionary

## Evidence layers

| Layer | Source and transformation | Interpretation |
| --- | --- | --- |
| Patient-entered money | Medical and other payments, one reporting period | Self-reported spending, not proven Lyme-attributable cost |
| Work and care | Entered days missed and unpaid caregiver hours | Days and hours remain separate from money |
| Work-loss scenario | Days missed × user-selected value per day | Modeled value; not added to patient-paid spending |
| Published references | Hook Table 5, societal costs in 2016 USD; Yu Table 2, medical episode/OOP references in 2022 USD | Different populations and perspectives; do not add them or infer diagnostic-delay savings |
| County illustration | NYSDOH reported cases × one published overall mean | Illustrative arithmetic, not measured county burden |
| Federal context | Local CDC tick/case workbooks; HRSA AHRF county capacity; Census contextual values; CDC PLACES where loaded | Geography, surveillance and general community context, not personal risk |
| Fictional example | Six authored cards in `burden_demo.py` | Synthetic, not collected; never combined with actual patient files |
| Survey archive | Previously supplied project-lead summary and Beta comparisons | Not independently recalculated from a current export; not headline evidence |

Hook 2022 numerical results were checked against the user-supplied public article
text on October 14, 2026 (Methods, Results and Discussion; linked tables were not
separately retrieved). Societal mean $2,032 and median $690 describe 613
participants in 2016 dollars. The patient-cost mean $1,252 and median $244
describe 901 participants and include productivity losses, rather than only
out-of-pocket payments. Suspected, undiagnosed and nonacute disease costs were
excluded. Details and source-text hash are in
`data/hook_2022_article_verification.json`. The county calculator defaults to
this societal reference; Yu medical mode remains separate. County case counts
were checked against the supplied NYSDOH 2024 cases PDF, page 5 (Dutchess 1,060;
Orange 964). Original Yu tables still need verification. Project survey spending
thresholds and time-loss counts are a separate evidence layer, not additional
dollar amounts to sum with these references.

The observed county-rate chart uses Mid-Hudson CHA 2025 Figure 147, page 219,
for 2022–2023 and the checked NYSDOH 2024 rates PDF, page 5, for 2024. It excludes
pre-2022 rates because of the surveillance definition change described in the
assessment. It remains separate from hypothetical future burden paths.

## Cost and time fields

| Field | Meaning | Missing handling |
| --- | --- | --- |
| medical88 | Money the person paid for medical care, including tests counted once | Blank stays unknown |
| other88 | Other spending such as transport and supplies, excluding medical payments | Blank stays unknown |
| Recorded patient-paid spending | medical88 + other88 | Incomplete if either is unknown; no automatic zero |
| workdays88 | Reported days of missed work in the chosen period | Blank stays unknown |
| caregiver88 | Unpaid caregiver hours in that period | Remains hours unless separately valued |
| dayvalue88 | Chosen value per missed workday | Scenario assumption, not measured income |
| period88 | Past 30 days, past 90 days, since symptoms started, or not reported | Different periods are not combined |
| phase88 | Before diagnosis, after diagnosis, both, or not reported | Recording phase; not a clinical stage |
| patient88_county | Confirmed county of residence | ZIP is not automatically treated as residence |
| barrier88 | Main reported care/support barrier | Not reported is excluded from published distributions |

## Pilot contribution schema

The optional v88 pilot stores county FIPS, phase, period, medical/other cost
bands, workdays, caregiver hours, barrier and consent time. It does not store
raw stories, ZIPs, exact dollar payments or edits to the visit summary. Legacy
schemas remain intact. Production collection needs private durable storage,
reviewed consent, access control, retention/deletion, duplicate handling and
privacy-reviewed publication.

The local summary requires comparable residence/phase/period groups. Time
medians need five usable responses. An entire categorical distribution is
withheld if any category has fewer than five. These rules alone do not prevent
all disclosure, especially through repeated releases. Since-symptoms-started
entries are not treated as a fixed comparable period. No new production
collection or automatic publication was enabled in this release.

## Testing guidance

The Lyme testing section explains preparation and lab vocabulary. It does not
read uploaded reports, diagnose disease, order tests, estimate a person's
insurance payment or send report data to AI. CDC clinical guidance is linked.
Prices require a written estimate from the actual lab/insurer; none are invented.

## Source verification still required

Original CDC/journal pages and the live ZIP service were blocked by the local
network proxy during development. Published costs, population denominators,
survey summaries and clinical content require a final source/clinical review.
File presence is not proof that every source row is current or independently
verified. Source years and scopes remain attached to displays and exports.
# Caregiver-assisted personal records

Care & Support identifies whether a record is completed by the person, with help,
or by a caregiver on their behalf. Optional daily-life selections describe the
person receiving care; a separate text field captures the caregiver's own words.
The downloaded card labels these sources. This is a personal-record aid, not a
validated proxy outcome measure or a clinical assessment.

These optional fields remain in session memory and the personal download. They
are not added to story-AI requests or community aggregates. Automatic burden
prefilling is disabled for caregiver-on-behalf records to avoid interpreting a
caregiver's first-person spending or work loss as the patient's. Existing shared
patient-report storage rejects caregiver-on-behalf entries pending a separately
designed, consent-based reporting pilot. No ME prevalence or local clinician
availability claims were added.

