# TOPx Phase 2 — PathwayAI: ready-to-paste answers

Matched to the supplied three-page submission form mockup on October 14, 2026.
This is draft submission text, not a claim that the form has been submitted.

## Solution Overview (MVP Demonstration)

**Format:** User-Facing Application. If multiple formats are allowed, Interactive
Visualization Tool also describes the community dashboard.

**Live demo, prototype, or working product:**

https://pathwayai.streamlit.app/

## Access instructions (if needed)

Open the app and choose a pathway. For the patient workflow, choose Care &
Support, enter fictional cost-and-time details for one period, then review and
download the visit and burden card. For the community workflow, choose Community
Burden & Action, compare Dutchess and Orange, and download the county cost
breakdown. Sources and assumptions are in the bottom notes. External story AI
can remain off during review.

## Results for the American People

**189 words / 250 maximum. Copy only the answer below.**

PathwayAI serves people planning time outdoors, people concerned about tick exposure, patients, caregivers, and community teams.

For the public, the workflow starts before illness: plan an outdoor visit, explore tick and Lyme information, learn how to prevent bites, and understand when to seek care after possible exposure.

For people experiencing illness, Care & Support helps organize their story, record medical and other payments over one reporting period, and track missed work and unpaid help. They can review and download a personal visit-and-cost card. Entries carry across pages, reducing repeated effort. Lyme testing education and ready-to-use support requests help people prepare for conversations about appointments, prices and assistance.

For community teams, the workflow starts with New York surveillance and a Dutchess–Orange comparison. Teams can inspect reported Lyme rates, a 2022–2024 rate series, and a downloadable cost illustration covering medical costs, other expenses and lost productivity. Published research and patient survey experiences provide separate layers of evidence.

The immediate benefits are practical prevention information, a personal record for care, and transparent evidence for community planning. The next step is a consent-based reporting pilot that reuses reviewed records to strengthen local evidence.

## Data, Tech & Evidence Driven Approach

**253 words / 300 maximum. Copy only the answer below.**

PathwayAI combines federal open data, state surveillance, published research and patient-reported experience to support outdoor planning, prevention, care preparation and community decisions. Federal inputs include CDC tick-distribution and historical county tick-borne case files, Census community context, and HRSA health-workforce capacity data. NYSDOH reported Lyme counts/rates and sampled tick observations provide state evidence; the Mid-Hudson community health assessment adds regional context.

The primary county cost illustration uses verified 2024 reported cases: Dutchess 1,060 and Orange 964. Applying Hook et al.'s weighted mean societal cost of $2,032 per participant gives $2.15 million and $1.96 million in 2016 dollars. The medical reference is $1,333; the $699 remainder combines other expenses and lost productivity. These deterministic calculations illustrate transferred study costs, rather than measured county spending. They retain source, dollar-year and assumption metadata in downloads.

The small project survey contributes reported experiences of spending, time lost and diagnostic waits. Its thresholds are not treated as average costs or extrapolated as county prevalence. Personal cards remain distinct from both published and modeled results.

The Streamlit application provides modular geography, testing education, cost calculations and evidence retrieval. The Research & Strategy Agent retrieves bounded public evidence summaries and checks citations; optional story AI requires opt-in. Public evidence analysis excludes private patient cards. AI aids organization and explanation, while calculations use explicit arithmetic.

NYSDOH figures were checked against supplied official PDFs; Hook figures against supplied article Methods and Results. Other references retain verification notes. Separate map views distinguish human Lyme rates from sampled tick observations.

Source links: https://www.health.ny.gov/statistics/diseases/communicable/2024/ and https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article

## Execution, Efficiency & Delivery

**215 words / 250 maximum. Copy only the answer below.**

PathwayAI is a working web MVP for the public, patients, caregivers and community teams. Its four pathways cover outdoor planning, tick-bite guidance, care preparation and community evidence.

It turns scattered information into outputs people can use: a reviewed card for a visit, a request for an itemized clinic estimate or appointment, and a county comparison with downloadable assumptions. Reusing existing entries reduces repeated form filling. Short and detailed reading options support different information needs.

For community teams, the two-county model makes costs visible by category. The combined societal illustration is $4.11 million in 2016 dollars, based on reported cases and a published study mean. Medical costs and the combined nonmedical/productivity remainder reconcile with that total. Teams can inspect the calculation instead of relying on an unexplained score. The model is a planning illustration, not a demonstrated local expense or return on investment.

Patient and network feedback guided improvements to wording, navigation, geographic matching, reading choices and repeat entry. All 26 automated tests passed in the development environment, with additional app checks of maps, exports and patient-record reuse.

These results establish technical functionality and concrete deliverables. Structured usability evaluation, improved care access, clinical outcomes and savings remain to be measured. Secure integrated community reporting is a planned pilot rather than an operating component of this MVP.

## Scalability, Reuse & Societal Impact

**247 words / 250 maximum. Copy only the answer below.**

PathwayAI is deployed on Streamlit from GitHub for people planning outdoor activities, people seeking care, caregivers and community teams. Modular code separates geography, evidence retrieval, testing education and cost calculations. Additional counties can reuse the workflow when compatible counts, rates, population context and reviewed cost assumptions are available. Broader disease coverage requires disease-specific evidence rather than transferring Lyme costs unchanged.

Personal entries are processed in server-side session memory. Shared collection is disabled by default. Entries are reused within the session and are not automatically submitted to community reports, the external survey or public evidence AI. Users review their card before downloading or sharing it; external story AI requires opt-in.

We are seeking clinics, community organizations and public-health partners for a consent-based local reporting pilot. It would reuse patient-entered records, agree reporting periods, check duplicates, and publish privacy-reviewed summaries. Controlled storage, access rules, retention policies and explicit permission must precede integrated shared collection.

Key assumptions include transferring historical study costs to reported county cases, comparable cost categories and periods, and the limited representativeness of voluntary survey participants. Persistent, suspected and undiagnosed illness require additional evidence. The model is not a complete lifetime burden estimate.

Next steps are partner-led usability testing, fuller accessibility review, additional source verification and evaluation of completed support connections. The intended societal benefits are informed outdoor preparation and better visibility of financial pressure and support needs, helping communities target prevention and care resources. Outcomes, adoption and sustainable operating arrangements will be evaluated with pilot partners.

## Final checks — do not paste as a form answer

- Confirm the live URL works signed out and uses `main`, lowercase `app.py`.
- The privacy statements describe code defaults; verify the live deployment
  retains shared collection disabled. Free text may receive identifiers despite
  the app's instruction to omit them.
- The Google Forms survey is separate; its live consent/privacy settings have
  not been verified here.
- Phone, keyboard and screen-reader audits and a backup demo recording are not
  represented as completed.
- Census-based disability context is secondary-source data with an unresolved
  citation-year conflict. Yu original-table verification remains outstanding;
  the primary county totals above use the checked Hook reference instead.
- Review team/eligibility declarations yourself. This mockup does not show those
  fields or provide the complete judging rules.
