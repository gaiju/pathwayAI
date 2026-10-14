# PathwayAI — submission draft

The actual form mockup has now been supplied. Use
[TOPX_PHASE2_READY_TO_PASTE.md](TOPX_PHASE2_READY_TO_PASTE.md) for the four exact
questions and verified word limits. This earlier draft is background material.

Prepared October 14, 2026. Field names below are provisional until the actual
submission questions and word limits are supplied. Team names, eligibility,
contact information and declarations must be completed by the entrant.

## Project name

PathwayAI

## Tagline

Prevent bites. Find timely care. Make hidden costs visible.

## Challenge area

Cost of Illness is the strongest current fit. The prevention and visit-preparation
features also support Lyme Innovation. Select the category that matches the
team's accepted entry and the organizer's form.

## Overview

A tick bite can lead to more than a medical bill. Illness can disrupt work,
travel, caregiving and family life. These effects are scattered across public
data, research papers and individual experiences.

PathwayAI brings them into one accessible web application. People can prepare
for outdoor activities, learn what to do after a bite, prepare a visit summary,
and keep a personal cost-and-time card. Community teams can compare reported
Lyme rates and examine transparent, study-based cost illustrations.

The MVP focuses on Lyme disease, with a Hudson Valley comparison of Dutchess
and Orange counties. It helps people organize their experience and gives
community teams a traceable starting point for prevention and support planning.

## Intended users and immediate benefit

Patients and caregivers receive a reviewed, downloadable card with their
story, money paid, missed work and help needed. Entries are reused across
pages, reducing repeated work. Testing guidance and tailored support-request
templates help them prepare for conversations with clinics and services.

Community organizations, clinics and public-health teams can compare county
reports, review published costs and download a cost breakdown with its sources
and assumptions. They can use these outputs to discuss local needs and plan
what to measure. Health outcomes and savings still require evaluation.

## Data, technology and AI

PathwayAI uses federal CDC tick-distribution and historical county tick-borne
case files, Census community context and HRSA health-workforce capacity data.
NYSDOH counts, rates and sampled tick observations add state-level evidence.
Regional health assessments add local context, while peer-reviewed Lyme cost
research supplies economic reference values.

The Streamlit application separates personal entries, public observations,
published study findings and modeled illustrations. Cost arithmetic is
deterministic and downloadable. The Research & Strategy Agent retrieves bounded
public evidence summaries and checks source citations before returning an
answer. Optional story AI helps organize a user's account only after opt-in.
Public evidence analysis receives public evidence rather than private patient
cards. AI supports explanation and organization; it does not establish a
diagnosis or generate the underlying county cost calculations.

## Results and current evidence

The MVP offers four working pathways: outdoor prevention, next steps after a
tick bite, care and support, and community burden. Patients can review and
download a cost-and-time card, use a fictional testing example, and copy a
support request. The Community page shows separate Lyme-rate and tick-observation
maps, a 2022–2024 reported-rate series, and a Dutchess–Orange cost comparison.

Verified 2024 reported Lyme counts are 1,060 for Dutchess and 964 for Orange.
Applying Hook et al.'s $2,032 mean societal cost per participant gives
illustrative totals of $2.15 million and $1.96 million, respectively, in 2016
dollars. The model separates medical costs from the combined remainder for
other expenses and lost productivity. These are study-based illustrations,
not measured county spending or demonstrated savings.

The supplied 33-respondent project survey adds experiences of financial
pressure, time lost and diagnostic waits. Its voluntary sample is kept
separate from county prevalence and monetary estimates.

All 26 automated tests passed in the development environment. Representative
app checks also covered navigation, map views, downloads and reuse of personal
entries. These establish technical functionality, not clinical effectiveness.

## Patient feedback and accessibility

Feedback highlighted literacy, cognitive difficulty, repeat entry, confusing
geographic labels and unclear benefits. The app now offers short or detailed
reading views, plain-language pathways, reused records, clearer map measures,
and supporting methods at the bottom of pages.

Patients can choose their immediate need before reading longer explanations.
The app uses labeled controls and readable tables. A formal reading-level,
screen-reader, keyboard and mobile accessibility audit remains part of further
evaluation. Feedback informed design changes; it is separate from a structured
usability or clinical-outcome study.

## Privacy and responsible use

Personal entries are processed in server-side Streamlit session memory.
Shared collection is disabled by default. App records are not automatically
submitted to community reports, the external project survey or public evidence
AI. Users review their card before downloading or sharing it and are asked to
leave identifiers out of free text.

Optional external story AI requires opt-in. The external Google Forms survey
is a separate collection channel with its own consent and privacy settings,
which require review. API credentials remain in deployment secrets rather
than source code. An integrated community-reporting pilot requires explicit
consent, private storage, access and retention rules, duplicate checks and
privacy-reviewed summaries.

## Deployment and next steps

The MVP is deployed as a Streamlit web application connected to GitHub. Its
modular code separates geography, evidence retrieval, testing education and
cost calculations, making targeted updates easier to review and test.

We are seeking community groups, clinics and public-health partners for a
consent-based reporting pilot. The next step is to reuse reviewed patient
records for comparable local summaries, with agreed reporting periods and
privacy safeguards. Evaluation should measure whether people can complete
their card, prepare for care and connect with support, and whether community
teams find the evidence useful. Clinical benefit and cost savings need separate
validation.

Further work includes source verification, broader county coverage and
accessibility testing. Sustainable operating arrangements and funding will
be developed with pilot partners; no county adoption or financial commitment
is claimed.

## Reviewer access

Live app: https://pathwayai.streamlit.app/

1. Choose **I need care & support**. Use a fictional example or leave the story blank.
2. Enter cost and time for one period; review and download the visit and burden card.
3. Open **Community Burden & Action** to compare Dutchess and Orange and inspect the cost breakdown.
4. Download the two-county comparison; open bottom sources and assumptions.

External story AI can remain off for this walkthrough. Confirm anonymous access
in a signed-out browser before submission; local verification of live access
was blocked by this environment. Network testers previously reported no login
prompt. A short backup demo recording remains to be prepared using fictional
entries.

## Source notes and verification limits

- NYSDOH 2024 reported cases and rates: supplied original PDFs, page 5, checked
  October 14, 2026. County counts are surveillance reports rather than all
  infections or exposure locations.
  https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf
  https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf
- Hook et al., *Emerging Infectious Diseases* (2022): Methods, Results and
  Discussion checked against supplied public article text. Linked tables were
  not separately retrieved. Costs are in 2016 dollars; suspected, undiagnosed
  and nonacute illness were excluded. The $699 nonmedical/productivity remainder
  is calculated as $2,032 minus the $1,333 societal medical mean. It does not
  separately price travel and lost productivity.
  https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article
- Mid-Hudson CHA 2025: supplied report, Lyme Figure 147, page 219. Pre-2022
  rates are excluded from the trend because of the surveillance definition
  change. Its Census-based disability table has an unresolved heading/citation
  year conflict and is labeled as secondary-source context.
  https://www.dutchessny.gov/Departments/DBCH/Docs/MHRCHA2025.pdf
- CDC Lyme surveillance and HRSA AHRF:
  https://www.cdc.gov/lyme/data-research/facts-stats/index.html
  https://data.hrsa.gov/topics/health-workforce/nchwa/ahrf
- Census county context:
  https://www.census.gov/quickfacts/dutchesscountynewyork
  https://www.census.gov/quickfacts/orangecountynewyork
- Yu medical-cost figures displayed in detailed references remain pending
  original-table verification and are not the basis of the primary societal
  results above. The project survey is a supplied aggregate summary, not a
  newly verified raw-data analysis. No population-representative county patient
  estimates, proven AI accuracy, clinical outcomes or savings are claimed.
