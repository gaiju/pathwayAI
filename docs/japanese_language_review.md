# Early language selection and Japanese review build

Prepared November 6, 2026. Review branch only: `feature/early-language-japanese`. Not merged or deployed. Subsequent development, not a claim about the original HHS submission.

## User-facing changes

- Show all 13 named note languages plus “Other / not sure” at entry, before forms. English, Spanish, Chinese, French, Haitian Creole, Arabic, Vietnamese, Tagalog/Filipino, Korean, Russian, Portuguese, Hindi and Japanese remain available.
- Explain that menus remain mainly English; the selector is for notes and visit preparation, not a full interface translation.
- Synchronize early and in-form language selectors using the existing saved note preference. Keep original notes and burden records; drop stale translation results after an explicit language change. No language change triggers an AI request.
- Add Japanese introductory guidance and consent/button text. These draft strings require native-speaker review before claiming verified Japanese localization.
- Add a licensed, embedded Noto Sans CJK JP font. Use it for Japanese text and shared kanji when Japanese is selected; detect kana for direct PDF calls without a preference. Preserve existing renderer behavior for other scripts and original text.
- Original-note PDFs include the writing-language label. Bilingual PDFs already identify the language and preserve the original alongside the user-reviewed English summary.

## Scope and dependencies

This branch is based on published `5c0c418` and integrates the previously prepared multiscript PDF fix because the published renderer does not provide portable CJK font embedding. It does **not** include county report version 1.12 or the pending county evidence-gap changes.

The PDF dependency change introduces WeasyPrint/Pango/HarfBuzz and licensed fonts for Chinese, Korean, Arabic, Hindi and Japanese. `packages.txt` lists native host dependencies. Technical tests run locally; production installation remains unverified until an approved deployment. Font binaries increase repository size; PDFs use font subsets.

No symptom illustrations, image uploads, medical interpretations, diagnosis tools, data changes, AI model changes or extra API requests are introduced. Symptom illustrations remain a separate content/licensing/medical-review task.

## Main files

`app.py`, new `language_preferences.py`, `language_organizer.py`, `report_download.py`, `pdf_report.py`, `multilingual_pdf.py`, fonts/licenses, dependency manifests and focused tests.

## Reviewer preview

`docs/review/japanese/PathwayAI_Japanese_Fictional_Sample.pdf` is a **hand-prepared expected-output example**, not evidence of a live AI translation. It includes fictional Japanese notes, a sample English summary, a negative test, location uncertainty and spending. Native readers should check the UI copy, the preserved original, summary meaning, kanji appearance and download readability.

Screenshots show desktop/mobile homepage selection and mobile note entry. The original-note browser PDF is produced through the actual local download flow. No real patient data or live/billable AI calls were used in these checks.

## Validation and remaining review

- Four focused tests cover record preservation, cross-route preference/translation persistence, explicit permission, stale-result removal, Japanese payload integrity, original-text preservation, font coverage/embedding and text extraction. Translation is mocked, so these tests do not establish real model translation quality.
- Seven existing organizer tests passed after adding Japanese.
- Chromium checks cover desktop 1440 px and mobile 390 px: early Japanese selection, care navigation, no horizontal document overflow, original-note PDF download and text extraction. The mobile sidebar is closed for the homepage preview.
- Sample PDF rendered with Poppler for visual inspection. This is not native-speaker or all-viewer validation.
- Japanese-speaking reviewer still needs to review instructions and live fictional translations for negation, approximate dates, medication/place names, uncertainty and costs. Adobe/mobile-reader and assistive-technology checks remain manual review items. Preferences last within the server session; clearing the session resets them.

## Final results

Full regression suite: **134 tests passed in 163.103 seconds**, including the new Japanese tests and existing multiscript/font/security tests. Three PDF-feedback regression tests were also rerun after the original-note language label change and passed. `git diff --check` passed. Existing Streamlit deprecation and fontconfig cache warnings did not fail the tests. These are technical checks, not clinical or native-language validation.
