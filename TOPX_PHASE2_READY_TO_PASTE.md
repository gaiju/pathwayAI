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

**213 words / 250 maximum. Copy only the answer below.**

PathwayAI serves people planning outdoor activities, people concerned about tick exposure, patients, caregivers and community teams. It supports the journey from prevention to care, support and community action.

Before illness, people can plan an outdoor visit, explore tick and Lyme information, learn how to prevent bites and recognize when to seek care. For people experiencing illness, Care & Support helps organize their story, record medical and other payments over one period, and track missed work and unpaid help. Users review and download a personal visit-and-cost card. Entries carry across pages, reducing repeated effort. Testing education and ready-to-use requests help people prepare for conversations about appointments, prices and assistance.

Community teams can compare Dutchess and Orange reported Lyme rates, inspect a 2022–2024 rate series and download a study-based cost breakdown. Public reports, research and patient experiences remain distinct evidence layers.

The immediate benefits are practical prevention information, preparation for care, support resources and transparent evidence for planning. The next step is a consent-based pilot with community organizations, clinics and public-health teams. It would reuse reviewed records so patient voices can inform decisions about care barriers and support.

The long-term goal is fewer preventable Lyme cases, more timely appropriate care and less financial and daily-life burden for people, families and communities. Those outcomes require evaluation.

## Data, Tech & Evidence Driven Approach

**270 words / 300 maximum. Copy only the answer below.**

PathwayAI combines federal open data, state surveillance, published research and patient-reported experience to support prevention, timely care, support and community decisions. Federal inputs include CDC tick-distribution and historical county tick-borne case files, Census community context and HRSA health-workforce capacity data. NYSDOH reported Lyme counts/rates and sampled tick observations provide state evidence; the Mid-Hudson community health assessment adds regional context.

The county cost illustration uses verified 2024 reported cases: Dutchess 1,060 and Orange 964. Applying Hook et al.'s weighted mean societal cost of $2,032 per participant gives $2.15 million and $1.96 million in 2016 dollars. The medical reference is $1,333; the $699 remainder combines other expenses and lost productivity. These deterministic calculations transfer study costs to county case counts; they are not measured local spending. Downloads retain source, dollar-year and assumption metadata.

The small project survey adds experiences of financial pressure, time lost and diagnostic waits. Its thresholds are not treated as average costs or extrapolated as county prevalence. In a future consent-based pilot, reviewed local records could help partners identify care barriers and evaluate support needs over consistent periods.

The Streamlit application separates personal cards, public observations, published findings and modeled illustrations. The Research & Strategy Agent retrieves bounded public evidence summaries and checks citations. Optional story AI requires opt-in; public evidence analysis excludes private patient cards. AI supports organization and explanation, while calculations use explicit arithmetic.

NYSDOH figures were checked against supplied official PDFs; Hook figures against supplied article Methods and Results. Other references retain verification notes. Separate maps distinguish Lyme rates from sampled tick observations. Community partnership and evaluation are needed to translate these insights into practical responses.

## Execution, Efficiency & Delivery

**223 words / 250 maximum. Copy only the answer below.**

PathwayAI delivers a working web MVP across the journey from prevention to care, support and community planning. Four pathways serve the outdoor public, people concerned about a bite, patients, caregivers and community teams.

It turns scattered information into practical outputs: outdoor preparation guidance, a reviewed visit-and-cost card, a clinic or support-service request, and a county comparison with downloadable assumptions. Reusing entries reduces repeated form filling. Short and detailed reading options support different information needs.

The Dutchess–Orange model makes medical costs, other expenses and lost productivity visible. Its combined societal illustration is $4.11 million in 2016 dollars, based on reported cases and a published study mean. The components reconcile with the total. Teams can inspect the calculation and discuss support priorities. This is a planning illustration, not measured local spending or demonstrated return on investment.

Patient and network feedback guided wording, navigation, geographic matching, reading choices and repeat entry. All 26 automated tests passed in the development environment, alongside representative app checks of maps, downloads and record reuse.

The next delivery step is a community-partner pilot linking reviewed patient experiences with practical responses to financial, travel and care-access barriers. Patient voices should inform both the response and its evaluation. The long-term aim is fewer preventable infections, more timely appropriate care and reduced burden. Clinical outcomes, completed support connections and savings remain to be measured.

## Scalability, Reuse & Societal Impact

**236 words / 250 maximum. Copy only the answer below.**

PathwayAI is deployed on Streamlit from GitHub. Modular code separates geography, evidence retrieval, testing education and cost calculations. Additional counties can reuse the workflow with compatible surveillance, population context and reviewed cost assumptions. Other illnesses require disease-specific evidence.

Its long-term impact depends on adoption and evaluation with community organizations, clinics and public-health teams. We are seeking partners for a consent-based reporting pilot that reuses reviewed patient records, gives patient voices a role in decisions and identifies practical barriers to care and support. Partners would test responses and track whether people reach the help they need.

Personal entries are processed in server-side session memory. Shared collection is disabled by default. Records are not automatically submitted to community reports, the external survey or public evidence AI; external story AI requires opt-in. Integrated reporting requires explicit permission, private storage, access and retention rules, duplicate checks, consistent periods and privacy-reviewed summaries.

Key assumptions include transferring historical study costs to reported county cases and the limited representativeness of voluntary survey participants. Persistent, suspected and undiagnosed illness require additional evidence; the model is not a complete lifetime burden estimate.

Next steps include partner-led usability testing, accessibility review, source verification and evaluation of support connections. The goal is to turn prevention information and patient experience into action: fewer preventable Lyme cases, timely appropriate care, fewer access barriers and less burden on people, families and society. Outcomes, adoption and sustainable operating arrangements need evaluation.

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
