# Community action summary — review only

## Scope and provenance

Prepared November 1, 2026 (America/New_York). This is a subsequent development update, not a claim about features present in the originally submitted HHS MVP.

Inspected GitHub main at `9d44822`, the deployed-source branch. The Streamlit entry point is `app.py`; `policy89()` renders Community Burden & Action. The existing four tabs, county comparisons, care navigation and patient tools are retained. Earlier county-report review branches were deliberately not merged into this work. The live deployed commit cannot be verified from this restricted environment.

Source inspection:

- NYSDOH stored verification files provide 2024 Dutchess/Orange counts and rates, plus the state comparison. No denominators are reconstructed and no latest-data claim is made.
- Existing CDC county files cover 2019–2022. They remain historical context, separate from NYSDOH 2024; no overlapping case totals are combined.
- The existing HRSA AHRF 2024–2025 ZIP provides 2023 primary-care physician, hospital and bed counts. These are general resources, not demonstrated care access, appointments, Lyme expertise or shortages.
- Hook et al. (2022) supplies the existing 2016-dollar societal-cost illustration. Arithmetic, case counts, original dollar year and optional CPI method are unchanged.
- The October 3, 2026 project-lead-supplied survey snapshot describes 33 self-reported diagnosed respondents. It is small and self-selected across locations. Raw responses, question-level denominators and cost/time periods are not verified here. Only aggregate context and previously described themes enter the brief; no new percentages, local extrapolation or patient records.

## Changes

- `app.py`: calls the new summary before the existing community tabs and passes the selected audience to the county brief.
- `community_action_summary.py`: four nonclinical action areas, three audience choices with three suggestions each, evidence explanations, and source-backed HRSA loading with explicit missingness.
- `county_burden_report.py`: adds audience actions, HRSA resources, survey context, preparation date, evidence labels and sources to the existing PDF/CSV exports. Public evidence, published estimates, survey context and proposed actions stay separate.
- `pdf_report.py`: reuses the existing multilingual PDF renderer with optional public-report footer and clickable standalone HTTPS URLs. Defaults for all personal PDFs are unchanged.
- `tests/test_community_action_summary.py`: verifies selected-county loading, zero versus missing values, audience changes, evidence separation, preserved comparisons/downloads and private-record exclusion.
- `docs/review/`: desktop/mobile screenshots and an Orange County preview PDF for patient advocacy organizations.

No source datasets, homepage, clinical guidance, AI service settings, patient input fields, storage settings or multilingual organizers are changed. No new PHI collection, analytics, risk scores, predictions or rankings are added.

## Verification

- Streamlit starts locally on port 8547.
- Targeted new/existing community tests: 5 passed.
- Browser: 1440px desktop and 390px mobile; summary, audience selection, Orange selection and PDF download; no application exceptions or page-level horizontal overflow.
- 60 PDF combinations (2 counties × 5 priorities × 3 audiences × 2 inflation settings) generated successfully. PDFs span 3–4 pages. Sources have 5 clickable links, or 6 with the optional CPI comparison. Selected audience, county, survey limits and original economic calculations are retained; extracted text stays within page bounds.
- Baseline full suite at unmodified `9d44822`: 96 tests, 93 pass, 3 existing errors from stale Care & Support expectations. These refer to the removed `care_to_tick_bite` control and outdated care/cost headings. They are not new runtime failures. Final branch: 99 tests, 96 pass, the same 3 pre-existing errors; no additional failures.

## Remaining limitations

- Source release currency, exact rate denominators and survey question-level denominators are not freshly verified. Do not describe 2024 as the latest available year.
- AHRF resource counts are historical context, not a directory of currently available services.
- The survey cannot establish county or U.S. prevalence, costs, demand, causality or savings.
- Suggestions require residents and qualified local partners to verify services, capacity, funding and responsibilities.
- Browser/PDF/usability checks are not clinical validation or proof of improved outcomes.
- Existing Streamlit `use_container_width` deprecation warnings remain; a framework migration is outside this change.
- No merge or deployment is authorized by this review branch. Publishing requires the owner's approval.
