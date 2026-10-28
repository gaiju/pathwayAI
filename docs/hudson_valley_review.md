# Hudson Valley community experience — review branch

## Scope

This change is prepared on `audit/community-burden-review`. It is for review, not an adopted county program or verified production deployment. The demonstration covers Dutchess and Orange only; it does not estimate the entire Hudson Valley's burden. No source data files, real patient information, collection settings or patient-support defaults are changed.

## What changed

- A clearly named landing route opens on the Hudson Valley regional context.
- Four short, mobile-friendly navigation labels connect Region, Compare, Burden and Plan.
- Existing comparison tools retain multi-selection, independent units and zero baselines. The New York map is optional in simple mode.
- The existing county report is the primary planning output. Additional legacy templates are collapsed, retained and kept separate from the primary report.
- A shared source-backed module supplies the two counties' counts/rates, contextual language measures and selected historical HRSA capacity fields. Source-unavailable values remain missing rather than zero.
- The structured two-page public-data brief includes the neighboring county, statewide reported rates, original-year societal arithmetic, optional qualified inflation comparison, local resource context, social burden coverage, feasibility checks and follow-up questions. Source links are clickable. Patient PDF rendering is unchanged.
- Three stale tests now check the current headings and sidebar route, preserving their original care-access, ordering and record-retention purposes.

## Scientific boundaries

- NYSDOH 2024 counts and rates are previously checked supplied source values; source pages were not freshly retrieved. Exact population denominator counts and vintage remain unverified, so official rates are displayed without reconstruction from a different population source.
- The 2022–2024 rate trend remains distinct from longer historical periods and hypothetical cost paths.
- Hook's USD 2,032 societal mean is a study reference, not measured county spending, an individual expected bill or a causal savings estimate. Its components are not added twice.
- The optional 2025 purchasing-power comparison still uses 11 observed months, with October missing; it is not a verified official annual-average restatement.
- HRSA counts concern 2023 general healthcare resources, not current availability, Lyme expertise or appointment capacity. Language spoken at home is not English proficiency or interpreter demand.
- All-cause disability context retains its unresolved source-vintage notice; no county Lyme disability probability is estimated.
- Project survey findings remain a voluntary cross-location snapshot with unresolved question-level denominators. No percentages or costs are extrapolated to county residents. Horn/Johnson study populations remain separate.
- Personal session records and synthetic demonstration cards are not included in the county report. Any future shared reporting needs its own governed consent and privacy process.

## Review and acceptance checks

Review the landing route, default regional view, selected comparisons, report county/priority controls, ordinary and adjusted PDF outputs, clickable citations, missing-data handling and public/private separation. Check desktop and phone views and preservation of multilingual patient flows. Record test results only after completion; local checks do not establish user validation, live deployment or improved health outcomes.


## Completed local verification

- Full suite: 99 tests passed (`python -m unittest discover -s tests -v`). The three pre-existing stale-selector errors were corrected, and three new community tests were added.
- Browser: landing-to-region route, default regional view, selected comparisons, report controls and PDF download verified locally.
- Mobile: fresh 390 × 844 page and desktop 1440 × 1000 checked; no page-level horizontal overflow, no visible exceptions, all four navigation tabs visible.
- PDF: both counties, original and optionally restated figures produce two-page public briefs; seven clickable sources, eight when CPI is included. Downloaded PDF text, resource values and comparison rows checked.
- Existing patient navigation, consent, multilingual organization, Russian/Vietnamese font handling, compact exports and saved-record regressions pass.
- Remaining limits: live deployed commit not verified; government-page retrieval blocked; source vintages and survey limitations remain as described above. Automated/local browser checks are not clinical or population validation. Streamlit emits existing deprecation warnings.
- No production deployment, main-branch merge, source-data modification or real-patient collection performed.
