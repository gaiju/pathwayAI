# PathwayAI Lyme disease burden evidence framework

PathwayAI | U.S. Lyme burden evidence and methods
Version: 0.2.0
Evidence review: 2026-10-23

PURPOSE
Connect county surveillance with published U.S. economic and functional evidence. Document measured, assumed and missing components.

NATIONAL CONTEXT
Hook reports annual national societal-cost illustrations of $345 million to $968 million in 2016 dollars. These historical reference points are not current spending or statistical confidence limits. The original national calculation is not recomputed here.

THREE DISTINCT QUESTIONS
Annual new-case burden: costs attached to a defined group of newly occurring cases over a specified follow-up period.
Ongoing population burden: costs and functional effects among people still affected, including earlier years of onset.
Lifetime burden: cumulative effects over a longer horizon; not estimated by this framework.

COST PERSPECTIVES AND DOUBLE COUNTING
Household payments, insurer-allowed medical spending and societal totals answer different questions. Hook societal totals already include medical, nonmedical and productivity components. Do not add the Adrion differences, patient payments or another work-loss estimate to them.
Adrion reports different adjusted comparisons over 12 months, not causal savings or lifetime cost. Claims cover commercially insured ages 0–64 in 2006–2010; a single common dollar year was not established in the reviewed text.

COUNTY CALCULATION
Reported cases × $2,032 Hook societal mean = a transfer-based illustration in 2016 dollars. Applying the study experience to a county is an assumption, not a direct county measurement.
Dutchess: 1,060 reported cases × $2,032 = $2,153,920. Orange: 964 × $2,032 = $1,958,848. Reported case year: 2024.
Case source: https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf

FUNCTION AND DISABILITY
Johnson describes selected persistent-illness respondents. Horn describes selected early-care follow-up participants. Neither supplies a directly transportable probability of county Lyme disability. All-cause HRSA/Census disability stays separate.

INTERNATIONAL COMPARISON
Country comparisons need compatible case definitions, reporting coverage, time horizons, local unit costs and currency/price years. No global total is calculated. U.S. unit costs are not applied worldwide.
International surveillance discovery: https://www.ecdc.europa.eu/en/borreliosis (portal not freshly reviewed; not a numerical input).

BURDEN INVENTORY
Component: Medical care | Available evidence: Hook societal medical component; Adrion claims-based costs; entered patient payments | Coverage / next evidence needed: Different perspectives and horizons; current Lyme-specific county spending remains unmeasured.
Component: Travel and other household spending | Available evidence: Optional personal cost records; part of Hook nonmedical costs | Coverage / next evidence needed: Comparable local records and reporting periods; no representative county average.
Component: Work disruption | Available evidence: Missed workdays; optional valuation; Johnson selected survey | Coverage / next evidence needed: Reduced hours, stopped work, reduced effectiveness and duration; prevent overlapping loss estimates.
Component: Unpaid caregiving | Available evidence: Optional hours entered in personal records | Coverage / next evidence needed: Agreed time period and valuation method; no current county dollar estimate.
Component: Daily function and quality of life | Available evidence: Optional dated personal observations; Johnson survey; Horn follow-up | Coverage / next evidence needed: Repeated, standardized measures; symptoms, limitations and benefits receipt are different outcomes.
Component: Longer-term disability and continuing costs | Available evidence: Selected illness studies; separate HRSA/Census all-cause context | Coverage / next evidence needed: Appropriate probability, duration, affected population and incremental cost. Not estimated from three-month symptoms or selected-survey percentages.

FOUR-PART COUNTY EXPLANATIONS
STUDY-BASED COUNTY BURDEN ILLUSTRATION
REPORTED CASES: Dutchess, New York; FIPS 36027; 1,060 reported resident cases in 2024. Source: https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf
PUBLISHED COST: USD 2,032.00 per participant/episode, 2016 dollars; medical, nonmedical and productivity costs. Hook et al. (2022): societal analysis n=613; reported cases in four high-incidence U.S. states; recruitment 2014–2016. Source: https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article
CALCULATION ASSUMPTIONS: Reported cases × selected published unit cost. Transfer of study experience to the county is assumed. No underreporting or inflation adjustment. No local case-mix adjustment. Populations and periods differ. Keep medical, household and societal perspectives separate; do not add Yu and Hook totals or interpret their difference as savings.
ADDITIONAL BURDEN TO MEASURE: Complete pre-diagnosis history; continuing costs and disability beyond the study horizon; separately measured caregiver time and valuation; and effects in populations excluded from the source. Some components are already included in a societal mean: identify overlap before adding any new cost.
PROVENANCE: Cases: data/ny_lyme_cases_2024_verification.json, supplied NYSDOH PDF page 5. Costs: data/hook_2022_article_verification.json. See docs/burden_methodology.md; framework version 0.2.0.
STUDY-BASED COUNTY BURDEN ILLUSTRATION
REPORTED CASES: Orange, New York; FIPS 36071; 964 reported resident cases in 2024. Source: https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf
PUBLISHED COST: USD 2,032.00 per participant/episode, 2016 dollars; medical, nonmedical and productivity costs. Hook et al. (2022): societal analysis n=613; reported cases in four high-incidence U.S. states; recruitment 2014–2016. Source: https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article
CALCULATION ASSUMPTIONS: Reported cases × selected published unit cost. Transfer of study experience to the county is assumed. No underreporting or inflation adjustment. No local case-mix adjustment. Populations and periods differ. Keep medical, household and societal perspectives separate; do not add Yu and Hook totals or interpret their difference as savings.
ADDITIONAL BURDEN TO MEASURE: Complete pre-diagnosis history; continuing costs and disability beyond the study horizon; separately measured caregiver time and valuation; and effects in populations excluded from the source. Some components are already included in a societal mean: identify overlap before adding any new cost.
PROVENANCE: Cases: data/ny_lyme_cases_2024_verification.json, supplied NYSDOH PDF page 5. Costs: data/hook_2022_article_verification.json. See docs/burden_methodology.md; framework version 0.2.0.

DATED PATIENT RECORDS
Optional dated daily-life observations stay in the private app session and selected personal downloads. Observations are not automatically totaled, sent to AI, or included in public evidence packages. Overlapping periods remain separate. These custom preparation questions are not a validated disability instrument.

UNCERTAINTY AND EVIDENCE STATUS
Scenario ranges require documented assumptions. Statistical uncertainty needs an appropriate model; arbitrary ranges are not confidence intervals. Current references do not establish PathwayAI savings, resource-allocation effects or disability reduction.
Sources use different populations, periods and price years. New web downloads were blocked. Paper verification is based on supplied documents; original studies, not PathwayAI, generated the cited findings.
Hook excluded non-English speakers and nonacute disease. The evidence inventory therefore highlights important gaps for the communities PathwayAI aims to serve.

REFERENCES
Hook SA et al. (2022). Economic Burden of Reported Lyme Disease in High-Incidence Areas, United States, 2014–2016. Emerging Infectious Diseases, 28(6).
https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article
Review status: Previously reviewed supplied article text; linked tables not separately retrieved.
Use in PathwayAI: Societal cost components and county illustrations, with study population and dollar year preserved.

Adrion ER, Aucott J, Lemke KW, Weiner JP. (2015). Health Care Costs, Utilization and Patterns of Care following Lyme Disease. PLOS ONE, 10(2):e0116767.
https://doi.org/10.1371/journal.pone.0116767
Review status: Uploaded full PDF reviewed.
Use in PathwayAI: A separate 12-month medical-spending reference; never added to societal totals.

Johnson L, Wilcox S, Mankoff J, Stricker RB. (2014). Severity of chronic Lyme disease compared to other chronic conditions: a quality of life survey. PeerJ, 2:e322.
https://doi.org/10.7717/peerj.322
Review status: Uploaded full PDF reviewed; table/narrative discrepancies recorded.
Use in PathwayAI: Work changes and daily-activity topics in optional dated personal records; selected-survey percentages are not county disability probabilities.

Horn EJ et al. (2025). Lyme Disease Biobank: 10 years of 3 month follow-up visits from 2014 to 2023. Frontiers in Medicine, 12:1577936.
https://doi.org/10.3389/fmed.2025.1577936
Review status: Uploaded full PDF reviewed.
Use in PathwayAI: Dated follow-up preparation and questions about continuing needs; three-month symptoms are not long-term disability.

Sanders GD et al. (2016). Recommendations for Conduct, Methodological Practices, and Reporting of Cost-effectiveness Analyses: Second Panel on Cost-Effectiveness in Health and Medicine. JAMA, 316(10):1093–1103.
https://doi.org/10.1001/jama.2016.12195
Review status: Bibliographic reference and supplied summary; full article not retrieved. Framework is adapted, not a claim of complete Panel compliance.
Use in PathwayAI: Impact inventory and explicit perspectives, assumptions, uncertainty and provenance; adapted from the supplied summary rather than a claim of full cost-effectiveness analysis.

CITE THIS FRAMEWORK
Zhang, Y. (2026). PathwayAI: Lyme disease burden evidence framework (Version 0.2.0) [Software and methods]. https://github.com/gaiju/pathwayAI/tree/burden-evidence-v0.2.0
Cite the original study for its findings. This citation identifies software/methods, not a peer-reviewed study, government estimate, endorsement or DOI-registered archive.

## Illness situations and opportunities for support

The U.S. burden tab compares Hook localized and disseminated societal group means (2016 USD), with no transition probabilities or causal savings assigned. Separate situations cover tick bites without illness, continuing symptoms, and longer-term support. Horn follow-up, Adrion historical claims, and Johnson selected-survey findings remain separate evidence rather than components of one total. A public action table connects these situations to preparation tools and possible community support. SVG, PDF and CSV downloads contain only public study information and planning suggestions.


## Optional general-inflation comparison

The uploaded FRED CPIAUCNS workbook supplies 12 monthly observations for 2016 and 11 for 2025 (October missing). The optional comparison uses available-month means: 240.0071666667 and 321.943; factor 1.341389111297371. This is a disclosed general-purchasing-power comparison, not a verified official annual-average CPI restatement. No imputation is performed. Original study-year charts and patient entries remain unchanged. Only Hook societal references and the associated two-county illustrations are restated. CSV and PDF include provenance and missing-month treatment; other studies are not automatically adjusted.


## County burden and action report

The Plan community support tab exports a county-specific PDF and flat CSV with reported cases and rates, Hook societal arithmetic in original 2016 dollars, optional explicitly limited CPI restatement, missing burden dimensions, a selected proposed support decision, feasibility checks and follow-up measures. County selection changes official counts and rates; support selection changes proposed actions, not observed demand. The builder is independent of Streamlit session state and imports no patient records or synthetic demonstration cards. This is a reproducible discussion brief, not a comprehensive county burden estimate, funded plan or proof of savings. Formative usability evidence and retest status are documented separately in docs/usability_evidence.md.


## Hudson Valley report revision 1.1

The regional route presents Dutchess and Orange as the initial examples, not the whole Hudson Valley. Shared county source access is in county_evidence.py. The existing report builder now includes the neighboring county and statewide rates, 2023 HRSA resource counts, ACS 2020–2024 language context, source verification status and explicitly separate social burden evidence. The dedicated county_report_pdf.py produces public-data briefs with clickable references and an appropriate footer. It does not modify patient-report rendering or include session records. Official surveillance rates are retained: their exact denominator population and vintage have not been independently verified. See docs/hudson_valley_review.md for the complete review scope.
