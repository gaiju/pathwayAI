# Embedded multi-script PDF fix — review branch, November 4, 2026

## Problem and correction
The original audit confirmed Arabic shaping/RTL, Hindi glyph and Korean display failures. Chinese appeared in one local renderer but referenced STSong-Light instead of embedding a Chinese font; that did not establish portability, and a reviewer reported unreadability elsewhere. We do not infer that every original PDF or most viewers fail.

The new PDF path uses WeasyPrint/Pango for Chinese, Korean, Devanagari and Arabic text, with bundled licensed Noto font files and embedded subset fonts. Arabic runs remain together for shaping, paragraphs use the direction of their first strong character, and mixed Latin/script text is handled by the layout engine. Inputs are escaped as text. PDF resource fetching allows only exact bundled font paths and internally generated state-badge SVG data images; external and arbitrary local resource reads are denied. No patient text is sent to a new service. Plain Latin/Cyrillic reports and the county PDF renderer retain the existing ReportLab path. No data, AI translation, calculations or navigation changes.

## Deployment dependencies
requirements.txt adds WeasyPrint 68.1 (<69); packages.txt declares Pango, Fontconfig and HarfBuzz-subset native packages for Streamlit Cloud. requirements-dev.txt adds pypdf for PDF-object inspection in tests. Bundled Noto CJK SC/KR and Arabic/Devanagari fonts and OFL notices are included. CJK OTFs are standalone regional faces extracted without glyph edits from the installed Noto collection. Fonts increase repository size by roughly 32 MB; output PDFs are subsetted. The cloud dependency rebuild has not been performed or verified. A deployment must install native libraries; no broken-font silent fallback is introduced.

## Validation
- 123 tests passed in 165.490 seconds, including four new tests for font coverage/embedding, run grouping/direction, escaped input/restricted fetching, multipage wrapping, state badge and clickable URL preservation.
- Prior multilingual feedback/cost-period/compact-record tests passed.
- All 12 listed language samples generated PDFs, script fonts embedded, no out-of-page text. ReportLab retains an unused standard Helvetica resource; non-Latin script fonts are explicitly embedded.
- Chinese, Korean, Arabic and Hindi samples rendered with both MuPDF and the independent system Poppler engine; before/after visual samples inspected. These are technical sample checks, not all characters, all PDF viewers or native-reader/translation validation.
- Browser check: app startup, existing county navigation and unchanged four-page county download passed.
- Python compilation passed. Existing Streamlit deprecation and local font-cache warnings do not fail the checks.

Review artifacts: docs/review/language_pdf_fix/. The original audit samples remain historical evidence under language_pdf_audit/. No merge or deployment; approval required before publishing these dependency/font changes.
