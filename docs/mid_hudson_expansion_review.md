# Seven-county Mid-Hudson expansion — review only

## Scope

This extends the unmerged county-planning review branch. It is subsequent development, not a claim about the originally submitted HHS MVP. No merge or deployment.

The region is explicitly defined as Dutchess, Orange, Putnam, Rockland, Sullivan, Ulster and Westchester (the Mid-Hudson economic-development region). Broader usages of “Hudson Valley” differ; Albany, Columbia, Greene and Rensselaer are not silently included.

## Newly verified source evidence

The owner supplied the official NYSDOH `cases.pdf`, titled *Communicable Disease in New York State: Cases Reported in 2024*. Page 5, Lyme disease column, was checked using county-row/column text coordinates and a rendered view. The PDF SHA-256 matches the original source record. The public aggregate source PDF is archived at `data/evidence/NYSDOH_cases_2024.pdf`; the JSON retains original verification metadata and adds a seven-county verification record.

| County | FIPS | Reported cases, 2024 | Published rate per 100,000, 2024 |
| --- | --- | ---: | ---: |
| Dutchess | 36027 | 1,060 | 355.5 |
| Orange | 36071 | 964 | 237.0 |
| Putnam | 36079 | 294 | 299.2 |
| Rockland | 36087 | 461 | 135.3 |
| Sullivan | 36105 | 385 | 482.6 |
| Ulster | 36111 | 841 | 461.2 |
| Westchester | 36119 | 1,125 | 113.2 |

Rates reuse the previously checked 2024 county-rate snapshots. No count is reconstructed from rounded rates or unrelated population estimates. Reported disease is not all infections, individual risk or measured economic spending. No claim that 2024 is the latest release.

## Implementation

- `mid_hudson_counties.py`: central seven-county FIPS registry and source-backed surveillance availability.
- `community_action_summary.py`: existing AHRF healthcare loader supports all seven FIPS; existing audience actions remain unchanged.
- `county_planning_indicators.py`: regional/state comparisons, selected-county rates and AHRF insurance/poverty for all seven. Missing language snapshots, earlier trend points and directory records remain unavailable. No Dutchess data copied into another county.
- `county_burden_report.py`: seven county choices, explicit coverage table, source status and no-total behavior if a future case count is missing. Original arithmetic and optional CPI method retained.
- `county_brief_pdf.py`: seven-county comparison fits the three-page layout; missing indicators are explicitly unavailable, never zero.
- `app.py`: Sources page wording aligned with the verified seven-county coverage; existing two-county comparison charts and all patient/navigation workflows remain intact.
- Source evidence JSON, focused tests and review artifacts.

Language values (ACS 2020–2024) and 2022–2023 trend points are available only in the stored Dutchess/Orange snapshots. Other counties do not inherit those values. HRSA field years remain insurance 2022 and poverty/resources 2023. County initiatives exist only where listed and require local verification; absence of a directory entry does not imply absence of services.

## Validation

- Full suite: 105 tests, 102 passed, the same 3 pre-existing stale Care & Support test errors documented against unmodified main. No new failures.
- All 210 configurations (7 counties × 5 priorities × 3 audiences × 2 inflation settings) generated three-page PDFs with text within page bounds and unchanged case-count × USD 2,032 original-dollar calculations.
- Desktop 1440px and mobile 390px: select Westchester, verify 1,125 cases and 113.2 rate, download PDF, no application exception or page-level horizontal overflow.
- Missing-count edge case: no inferred count, no zero total, no CPI-restated county total when count is unavailable.
- Original personal records, language/PDF defaults, cost perspectives, inflation provenance and existing county comparison controls are retained. No new PHI collection or sharing.

## Review artifacts

- `docs/review/PathwayAI_Mid_Hudson_Seven_County_Review.zip`: seven PDF/CSV sets and scope note; review PDFs include the optional 2025 available-month purchasing-power comparison.
- `docs/review/mid_hudson/`: individual county briefs and methods.
- `docs/review/mid_hudson_coverage_desktop.png`.

These are study-based county illustrations, not measured spending, clinical recommendations, validated savings or adopted county programs. Newer Census estimates and broadband additions remain deferred. No county or organizational endorsement is implied.


## Owner-approved publication validation

The owner approved publication of the reviewed community and seven-county updates. Before publication, the three pre-existing stale Care & Support test expectations were updated to the current headings, transport wording and sidebar route; all original saved-entry, resource and bite-guidance checks were retained. The complete suite then passed: 105 tests, no errors. All seven browser county selections, mobile layout and the optional-comparison PDF download passed. The 210 export-layout checks remain valid. No patient/clinical application behavior was changed to satisfy the tests.

This supersedes the earlier review-only status for this approved release. GitHub main publication is separate from independent verification of the live Streamlit rebuild; live access is restricted in this environment.
