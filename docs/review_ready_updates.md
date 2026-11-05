# Review-ready downloads and county evidence gaps

Prepared November 5, 2026. These changes are subsequent development, not a claim about the originally submitted HHS MVP. Review branch only; not merged or deployed.

## Changes

- Integrate the previously prepared embedded-font PDF renderer for Chinese, Korean, Arabic and Hindi, with shaping and bidirectional layout. Keep the existing Latin/Cyrillic renderer. Include licensed fonts and native dependency manifest. Update the app's warm-process font revision guard.
- Preserve the county-specific, source-linked local-planning prompts and make their heading consistent across the app and PDF.
- Add a visible "What we still need to know" section in the county view and PDF, with the same gaps in TXT and CSV exports. Derive unavailable indicator labels from None values; zero remains a valid value. Do not infer why data are missing.
- Version county reports as 1.12, retaining four pages, references, original study-dollar calculations and optional partial-year CPI comparison. Tighten research formatting to accommodate the gaps without reducing the existing note font size.

## Main changed files

`app.py`, `county_burden_report.py`, `county_brief_pdf.py`, `pdf_report.py`, new `multilingual_pdf.py`, `requirements.txt`, `requirements-dev.txt`, new `packages.txt`, licensed font assets, focused tests and review artifacts. No dataset values, calculation formulas, navigation routes or AI requests changed.

## Validation

- All 210 county × priority × audience × inflation combinations generate four-page PDFs containing both planning and evidence-gap sections. Original case-count × USD 2,032 arithmetic checked for each combination.
- Two new tests verify county-specific gaps survive TXT/CSV export and that zero is not classified as missing.
- Real Chromium browser: Streamlit startup, navigation to community planning, PDF download and new section text. Desktop 1440 px and mobile 390 px have no document horizontal overflow. Screenshots included.
- Multiscript tests cover embedded sample glyphs, connected script runs, RTL paragraph selection, mixed wrapping, links and restricted local-font resource loading.
- See the final test result added below for the full regression suite.

## Remaining limits

Technical rendering tests do not establish translation fidelity, native-reader acceptance, clinical validation or universal PDF-viewer compatibility. Ask language testers to review real fictional-workflow exports before making broader accessibility claims. Native Pango/HarfBuzz dependencies must be present on the eventual host; production installation has not been tested because deployment is not authorized. Missing indicators remain unverified; no new sources or service availability were asserted. AppTest checks preserve existing patient workflows but are not a complete manual review of every feature.

## Review artifacts

`docs/review/review_ready/PathwayAI_Dutchess_Review.pdf`, `desktop.png`, `mobile.png`, `report_page3.png`. Existing synthetic multilingual samples are in `docs/review/language_pdf_fix/`.

## Final results

- Full regression run: **126 tests passed in 154.264 seconds**.
- New gap/export tests run separately: **2 passed**.
- County PDF layout/arithmetic matrix: **210 combinations passed**, all four pages.
- Chromium startup/navigation/mobile/PDF-download checks passed. Page 3 was also rendered with Poppler and visually reviewed.
- Existing Streamlit `use_container_width` deprecation messages and fontconfig cache warnings appeared; no test failures resulted.
- GitHub GraphQL API returned Forbidden, so an actual PR could not be created from this environment. The review branch is pushed; open https://github.com/gaiju/pathwayAI/pull/new/feature/review-ready-downloads to create it. No merge or deployment was performed.
