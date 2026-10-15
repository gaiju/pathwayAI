"""Source populations and periods; never infer survey response denominators."""

EVIDENCE_SCOPE = [
    {"Source": "Hook et al. (2022)", "Population / count": "613 societal-cost participants; 901 in the patient analysis",
     "Period / scope": "Recruitment 2014–2016; four high-incidence states; costs in 2016 dollars",
     "Key limit": "Separate analyses and denominators. Study costs are transferred assumptions, not measured county spending or full delayed-diagnosis costs."},
    {"Source": "Horn et al. (2025) / Biobank", "Population / count": "466 enrolled cases; 253 returned; 55 reported ongoing symptoms",
     "Period / scope": "Enrollment 2014–2023; median follow-up 89 days",
     "Key limit": "Early-care cohort and selected returners. Not representative of delayed-diagnosis burden; no economic costs measured."},
    {"Source": "PathwayAI survey snapshot", "Population / count": "33 respondents reported a diagnosis in the supplied summary",
     "Period / scope": "October 3, 2026 summary; voluntary participants across locations",
     "Key limit": "Current export, question-level denominators, missing answers and unique-person checks still need verification. Not county prevalence or an average cost."},
    {"Source": "NYSDOH county surveillance", "Population / count": "Dutchess 1,060; Orange 964 reported Lyme cases",
     "Period / scope": "2024 reports; county of residence",
     "Key limit": "Case counts, not survey sample sizes or exposure locations. Rates and modeled costs have different meanings."},
]
