# PathwayAI — reviewer and submission notes

Prepared October 14, 2026, from the supplied critique and current implementation.
This update changes documentation only. Review the final form's word limits and
the actual live deployment before copying claims into a submission.

## Access instructions: five-line reviewer path

1. Open https://pathwayai.streamlit.app/ and choose a pathway.
2. Patient view: **Care & Support → Record money and time → Review and download your visit and burden card**.
3. Use a fictional example; external story AI can remain off.
4. Community view: **Community Burden & Action → county comparison → Estimated community cost: Dutchess and Orange**.
5. Download the two-county comparison; open bottom sources for methods, survey findings and model assumptions.

## Deployment Strategy / Scalability: privacy sentence

Personal entries are processed in a private, server-side Streamlit session;
shared collection is disabled by default, and entries are not automatically
submitted to community reports, the external survey or AI services.

Additional detail if space permits: users can download their reviewed card.
Optional external story AI requires a separate opt-in and sends the supplied
story to the configured provider. The external Google Form has its own data
handling; its consent and collection settings have not been verified here.
An integrated reporting pilot requires explicit consent, controlled storage,
retention rules and reviewed aggregate release. Do not claim that all health
information stays exclusively on the user's device or that the app cannot
receive identifiers typed into free text.

## Data, Tech & Evidence

PathwayAI combines federal CDC tick-distribution and historical county
tick-borne case files, Census community context and HRSA health-workforce
capacity data with NYSDOH reported Lyme counts/rates and sampled tick
observations. Public regional health assessments provide additional local
context. These sources serve different purposes and retain their reporting
years and limitations.

The county societal-cost illustration multiplies verified 2024 reported cases
by Hook et al.'s weighted mean societal cost in 2016 dollars. It separates
medical costs from the calculated remainder for other expenses and lost
productivity. The patient's own card, published study results and modeled
county illustrations are distinct evidence types. Project survey findings
remain a separate, small voluntary-sample evidence layer.

The Research & Strategy Agent retrieves bounded public editorial evidence
summaries and requires source citations. Public evidence AI receives public
evidence, not private patient cards. Citation checks establish allowed-source
references, not the correctness of every generated claim. Dollar calculations
use deterministic arithmetic rather than LLM-generated estimates.

## Results: concise draft under 250 words

PathwayAI makes hidden costs easier to see through three distinct views:
personal entries, published study findings and transparent county-cost
illustrations. People can prepare a visit summary, record spending and time
lost, download a reviewed card, and use a tailored support request. Existing
entries are reused across pages.

Community teams can compare Dutchess and Orange reported Lyme rates, view a
2022–2024 reported-rate series, and download a study-based cost breakdown. Using
2024 reported cases and Hook's $2,032 societal-cost mean gives illustrative
totals of $2.15 million for Dutchess and $1.96 million for Orange, in 2016
dollars. These are transferable-study calculations, not measured local
spending, personal predictions or demonstrated savings. The small project
survey adds reported experience without being extrapolated as county
prevalence or added as dollar costs.

Automated testing covered 26 tests and representative application navigation,
map views and downloads. This is technical verification rather than clinical
validation or proof of improved health, faster diagnosis or savings. Patient
feedback guided plain-language presentation and reduced repeat entry. Secure,
consent-based shared reporting and evaluation with community partners are the
next pilot steps.

## Thirty-second demo script

“PathwayAI brings county Lyme reports, published cost research and patient
experience into one view. Here, a person keeps a cost-and-time card for care.
Here, community teams compare Dutchess and Orange. The county amounts are
2024 reported cases multiplied by a study cost in 2016 dollars; the sources
and assumptions are below. That makes medical costs and lost time visible
without presenting them as measured local spending. Our next pilot will reuse
consenting people's records to improve local evidence.”

## Suggested evidence slide

| Personal record | Published evidence | County illustration |
| --- | --- | --- |
| Money paid, missed workdays, caregiver hours, one reporting period | Reported Lyme counts/rates and study costs, with source and dollar year | Reported cases × study cost; explicit assumptions |
| Immediate benefit: reviewed card for care | Benefit: traceable evidence and context | Benefit: a starting point for resource planning and evaluation |

Place source links and methodological qualifications in slide notes or a
readable bottom source line. Keep year, scope and “illustrative” labels next
to the relevant values.

## Claims to correct in the supplied critique

- **Browser-only retention:** Streamlit's session state is server-side memory.
  A download creates a user-owned file; it is not the app's only handling of
  the data. The code's default collection setting does not prove the deployed
  environment's actual settings or hosting retention.
- **No identifiers by default:** free-text fields may receive identifiers even
  though the app asks users to omit them. Use the precise privacy sentence
  above rather than an absolute “no PHI” assertion.
- **Original cost tables checked:** Hook Methods/Results/Discussion were checked
  against user-supplied article text, not separately retrieved linked tables.
  NYSDOH counts and rates were checked against supplied original PDFs. Yu cost
  values remain pending original-table verification.
- **Current Census disability figures:** assessment-cited figures have an
  unresolved source-year conflict and are labeled as secondary-source context.
- **Accessibility:** plain language and reading choices are implemented. No
  formal reading-grade assessment, phone, keyboard or screen-reader audit is
  established. Do not imply a completed accessibility certification.
- **Public access and backup video:** network testers reported no login prompt,
  but this environment's live access was blocked. Confirm the submission URL
  in a private browser window. A backup video has not been created here.
- **Clinical outcomes:** users' ability to download cards and inspect calculations
  does not establish faster diagnosis, improved health, measured savings or
  adopted county policy.

## Remaining human checks before submission

Check the public URL signed out; make one phone and keyboard pass; record a
short backup demo using fictional entries; and confirm the deployed app uses
`main` and lowercase `app.py`. Show the main county comparison rather than
starting with an optional calculator. Include the original-table verification
status and accessibility limits accurately in the submission.
