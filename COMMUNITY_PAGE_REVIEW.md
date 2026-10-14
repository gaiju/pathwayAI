# Community page presentation review

The main view now follows one sequence: New York surveillance map, Dutchess–Orange comparison, costs and time lost, community actions, and a downloadable brief.

- The 2024 reported Lyme rates (Dutchess 355.5, Orange 237.0, statewide 109.8 per 100,000) were checked against the uploaded NYSDOH rates PDF, page 5.
- Hook cost figures were subsequently checked against the user-supplied public article text (Methods, Results and Discussion). The conceptual cost-category image remains. County counts were then checked against the supplied NYSDOH 2024 cases PDF, page 5. Original Yu cost tables still require verification. Published study references are not measured local costs.
- Hypothetical county calculations, future paths, group calculator, planning tables and AI remain available in collapsed sections.
- Methodological exclusions, development status and limitations appear in bottom notes. Short positive labels still distinguish study references, private records and illustrative calculations.
- Community action cards link to CDC tick prevention, HRSA health-center search and New York health coverage. Private records, consent, API configuration and production remain unchanged.
- The main narrative, discussion brief, cost-reference calculations and AI evidence scope cover both Dutchess and Orange. The supplied Dutchess health plan appears in a separately labeled local-context expander. Community Voice retains its privacy controls and allows either county to be selected.
- The cost graphic now reads “Lyme disease: the hidden costs” and “Money paid. Work missed. Unpaid care.”

## Reference sites for screenshot review

- CDC tuberculosis data: https://www.cdc.gov/tb-data/index.html
- New York communicable disease statistics: https://www.health.ny.gov/statistics/diseases/communicable/
- IHME disease burden visualization: https://vizhub.healthdata.org/gbd-results/

Live CDC and New York page requests were blocked by the environment's network proxy. These links are reference suggestions, not a completed inspection of their current layouts. User-supplied screenshots can support a direct design comparison. No content or data was copied from these sites in this change.

The user also supplied https://www.nih.gov/challenges/topx-hhs-tech-sprint-ai-invisible-illness . Its live page request was blocked by the same proxy. The subsequently supplied pasted text was read, covering overview, challenge areas, expected outcomes, prizes and timeline. It ends at “Phases”; the judging criteria were not included.

## Alignment with the supplied NIH challenge text

The stated goals emphasize functional MVPs, U.S. federal open data, AI and real-world usefulness for patients, caregivers, clinicians and decision-makers. The Cost of Illness area is PathwayAI's clearest current narrative: understandable cost categories, personal cost/time records, public-data comparisons and downloadable evidence. Lyme prevention and visit preparation support the Lyme Innovation area without establishing earlier diagnosis or measured outcomes.

The two-county view gives a coherent community audience without requiring a county partnership. NYSDOH and county plans are local/state context, not federal datasets. The existing CDC, Census and HRSA inputs must be identified separately in the submission, with their actual use described; links alone are not evidence of dataset integration. AI explains supplied public evidence; cost arithmetic is deterministic. Secure shared patient reporting, county adoption, savings and clinical effectiveness remain future validation work.

The supplied timeline lists Phase 2 closing October 15, 2026, 11:59 p.m. Eastern and demo showcase closing October 22, 2026, 11:59 p.m. Eastern, subject to organizer changes. Detailed judging criteria require the remaining page text.

Validation: all 20 existing tests passed, including first-click navigation. AppTest also exercised verified rate cards, both-county calculation tables, the separately labeled Dutchess plan, future-path controls, Community Voice county selection and downloads.

## Hook study evidence update

The Community page now shows the checked societal mean ($2,032), median ($690) and disease-group means ($1,307 localized; $3,251 disseminated; $2,620 probable), in 2016 dollars. The societal analysis included 613 participants. The patient-cost mean ($1,252) and median ($244), from 901 participants, include productivity losses and are not synonymous with money paid out of pocket.

The county calculator now defaults to a Hook-based societal illustration; its existing Yu medical-cost and case-mix modes remain available. Using the inherited 2024 case-count inputs gives Dutchess $2,153,920 and Orange $1,958,848 in 2016 dollars. These are reference-cost multiplications, with case-count verification still outstanding. Hypothetical path charts and exports retain the selected cost perspective and dollar year.

The RAG corpus includes a bounded public summary of the checked Hook methods, results and limitations, with verification metadata. It excludes the raw upload and all private patient records. The study's limitations are included: quota sampling, recall, excluded non-English speakers and excluded suspected, undiagnosed and nonacute disease. Neither diagnostic-delay savings nor county-representative patient burden follows from these results. The supplied project survey remains a separate evidence layer; threshold percentages do not establish an average dollar cost.

Validation for this update: 22 tests passed. AppTest exercised the checked cost metrics, both-county societal amounts, chart controls, preserved medical case-mix mode, switching perspectives and downloads.

## Patient-paid medical bills comparison

The study chart now uses matching blue and orange colors for separate societal and patient-paid medical-bill views, with an adjacent numeric table and source-tagged CSV. The medical-bill means are $314 (confirmed localized), $628 (confirmed disseminated) and $389 (probable), checked in the supplied article Results discussion of Figure 2. All amounts are in 2016 dollars. Medical bills represent one out-of-pocket category, not a total of all patient spending. Patient and societal analyses have different denominators; the bars are grouped, not stacked, and do not establish a patient-paid percentage or a county-specific out-of-pocket burden. These bounded public findings are also available to the RAG retriever.

## Four landing numbers and checked local inputs

All four existing headline figures now appear before the pathway choices: 476,000 estimated annual U.S. diagnoses/treatments; 62,551 reported U.S. cases in 2022; $345–968 million annual societal-cost illustrations in 2016 dollars; and 35% disabled work status in the selected persistent-illness study group. The study-group label stays beside the last figure; it is not general-population Lyme disability prevalence. The MyLymeData chartbook remains an inherited reference, not newly independently verified. Numbered source links and scope explanations are in a bottom footnote expander. Duplicate lower-page numeric cards were removed.

The supplied NYSDOH case-count PDF, page 5, confirms Dutchess 1,060 and Orange 964 reported Lyme cases in 2024. Those inputs are now marked checked in county exports. The uploaded Mid-Hudson assessment has a Lyme section on pp. 218–219 with rate data, not a county economic-cost estimate in that section. Figure 147 confirms the two comparison counties' 2022–2023 rates. The Community page combines these with the previously checked 2024 rates in an observed-rate chart and source-tagged download. Pre-2022 data is excluded because the assessment describes a 2022 surveillance definition break. No forecasting is performed on this observed series; hypothetical cost paths remain separately labeled.

Validation: all 23 tests passed. AppTest also verified exactly four landing metrics, bottom footnotes, patient-paid cost columns and downloads, the actual-rate trend, county selection and cost-perspective switching. Main, production, secrets, privacy controls and consent behavior were unchanged.

## Main county burden and categories

The county illustration is now prominently displayed after the observed-rate chart, rather than only inside a planning expander. It shows Dutchess $2,153,920, Orange $1,958,848 and the combined $4,112,768 in 2016 dollars. A stacked chart and table split the same societal reference into medical costs ($1,333 per participant) and the remaining other expenses plus lost productivity ($699 = $2,032 − $1,333). The residual combines two categories and is labeled as a calculated difference in the footer and export; the supplied overall figures do not support splitting it further. Patient-paid medical bills use a different analysis denominator and are not subtracted from the societal total.

The supplied project survey counts (14 of 33 reporting at least $10,000 paid, 18 of 33 over 100 days lost, 20 of 33 over five years to diagnosis) appear alongside the county model, labeled as across-location survey context. They are not extrapolated as county prevalence or added as dollar costs. Category averages and a common reporting period are needed to use this survey as a dollar-model input. The meaning of probable is explained beside the study chart and chart-axis labels are given enough space to remain readable.

Other possible research inputs identified for review: AHRQ MEPS (medical expenditure and patient-payment benchmarks), CDC/NCHS NHIS (work/function context), MyLymeData (selected persistent-illness patient experience), and BLS wage data (explicit productivity valuation assumptions). Live requests to all were blocked by the proxy. No new numerical estimates or verified study claims from those sources were imported. These sources require scope and sampling review before use as Lyme-attributable county inputs.

Validation: all 24 tests passed, including reconciliation of cost components with totals. AppTest checked the prominent county category table, both-county and combined metrics, separate survey context, probable definition and CSV download.

## Contribution choices and concrete support requests

The community invitation now offers independent choices: keep/review a personal cost-and-time record, or open the project lead's Google Forms survey. The external form URL was checked in the rendered app, but its live contents and privacy/consent settings could not be inspected because access was blocked. App records are not transferred into the survey and responses are not automatically included in community estimates. Secure integrated contribution remains a separate consent-based collection step, with reuse of entered fields.

Generic advice to ask a clinic about fees and accommodations was replaced by a need-specific request that users can copy or download. Cost requests ask for a written, itemized estimate and reduced-fee options; appointment requests ask about availability and referral requirements; transport requests ask about eligibility, timing and return trips; accessibility requests ask how to arrange support. Nothing is sent automatically and no appointment or eligibility is guaranteed. AppTest exercised cost and transport requests and the download, alongside the independent survey and personal-record routes.

Email alone does not implement consent-based county aggregation. Existing personal fields include actual medical/other payments, missed workdays, caregiver hours, period, care phase, residence county, and a separate tick-found location/date. Shared storage is disabled by default; the legacy consented CSV stores cost bands rather than actual amounts and cannot establish mean patient payments. Production aggregation requires an explicit consent record, controlled private storage, duplicate handling, comparable periods, reviewed county mapping and privacy-reviewed output. Tick observations must remain distinct from confirmed/probable disease surveillance.

## Landing disability replacement and Census-based context

The landing-page fourth figure is now the checked Hook societal mean of $2,032 per participant in 2016 dollars, replacing the selected-study 35% work-disability headline. Headline superscripts were removed; sources and scope stay in the bottom notes. The 35% reference remains confined to detailed study-population evidence.

The county comparison adds disability context from the supplied Mid-Hudson assessment, Table 12, printed/PDF p. 34: Dutchess 12.2%, Orange 11.7%. These are any-disability, all-cause figures cited to Census ACS S1810, not the under-65 QuickFacts measure and not Lyme-attributable disability. The report heading says 2023 while the source line says 2020 ACS five-year estimates; the original Census vintage has not been resolved. Labels therefore identify the figures as reported in the 2025 assessment, with that limitation in the bottom notes, provenance JSON and export. This is a secondary-source check rather than independent current Census verification.

AppTest verified the four revised landing values, absence of headline superscripts, the disability comparison and its bottom scope note.

## Public-data demonstration and clear map measures

The Community map now defaults to a single-measure 2024 reported Lyme rate map. Darker blue corresponds to higher reported human cases per 100,000 residents. All 57 county rows outside NYC were parsed from the supplied NYSDOH rates PDF, page 5, and matched to the existing New York boundary names. The source gives NYC as one aggregate, so the five borough counties are gray and that aggregate is not assigned to each borough. Essex has the largest rate in these 57 source rows; Dutchess is not labeled as statewide highest.

Users can switch to sampled tick observations. This separate view suppresses the older case-circle overlay. Comparison values retain their own reporting years and sampling limitations. The original combined-map behavior remains available to legacy callers, while the active Community view separates the measures.

The main contribution invitation now offers a private personal cost-and-time record for care. The external project survey link remains inside the bottom survey findings expander, with a Google Forms notice and consent/privacy review instruction. Tick details describe their immediate benefit in a visit summary instead of implying community collection is operational. Existing record reuse and the partner enquiry section remain intact.

The cost image now describes four burden categories in plain sentences rather than giving measurement instructions. The unpaid-care card says “Time family and friends spend helping.” Measurement rules and source limitations stay in the bottom notes.

Validation: 26 tests passed. AppTest exercised both map views, suppression of historical circles in the tick-only view, the bottom survey link, and the personal-record route. An additional geometry/source check confirmed all 57 county matches and the five separately reported NYC boroughs. The revised image was visually inspected for readable text and clipping.

## Simplified personal-story guidance

Patient feedback identified excessive choices and the risk of copying a fictional story into a personal account. Care & Support now leads with one story box and three short prompts: place/time, symptoms/duration, and care so far/help needed. It requests two or three sentences, permits skipping the story and retains the instruction to omit identifiers. AI assistance and a short read-only made-up example are collapsed after the box. The example autofill button was removed; no example is silently inserted into a personal record. The clear-session control remains available in the sidebar.

Optional external AI, local organization, summary downloads, detailed history and record reuse remain available. The anecdotal treatment account in the feedback was not used as clinical evidence or added to patient guidance. Plain-language wording was simplified without asserting a formally verified eighth-grade reading level.

Validation: all 27 tests passed, including a new regression check that examples do not prefill the story and that a person's own words survive a Community-page round trip.

## Verified Biobank evidence and acknowledgements

The full public Horn et al. paper was supplied and read. The bottom study-population section now identifies 253 returners from 466 enrolled cases, 55 reporting ongoing symptoms and 47 of 226 initially prescribed antibiotics reporting symptoms, with median follow-up 89 days. These public Table 5 findings are also in the bounded RAG summary, with verification metadata. The raw participant workbook and private analyses remain outside the repository, corpus and app.

No county totals or medication-cost estimates were changed. The study measures an approximately three-month symptom outcome, not county PTLDS risk or economic costs. An additional-cost extension needs justified cohort transfer, a defined follow-up window, nonreturner sensitivity and compatible incremental-cost evidence. Prescription costs require a price crosswalk and avoidance of overlapping baseline medical costs. Observational treatment recommendations were not imported into clinical guidance.

A bottom reading-list expander includes five relevant papers, with review status rather than claims about influence rankings or TOPx reviewer identities. Hook and Horn source contents were checked; Kugeler/Johnson citations were checked in Horn's bibliography but original contents still require review; Adrion remains a candidate original-paper review. A bottom acknowledgements expander credits patient/caregiver feedback and published Biobank/public-health research, without asserting endorsements or formal partnerships. Individual advisers are not named without confirmation and permission.

Validation: all 28 tests passed, including a RAG denominator/scope regression. AppTest verified the public study summary, reference list, acknowledgements and unchanged county cost totals.
