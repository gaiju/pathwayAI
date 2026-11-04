# PDF script-display audit — November 4, 2026

Scope: all 12 named note-entry menu options, using synthetic test sentences, the current report_pdf renderer, bundled-font character checks, PDF generation, text bounds and local rendered-page inspection. No AI translation calls or patient data. Synthetic multilingual sentences are font probes, not medically reviewed translations. No live deployment or cross-device claim.

Results:
- English, Spanish, French, Haitian Creole, Vietnamese, Tagalog/Filipino, Russian and Portuguese: sample primary-font characters covered and PDFs generated with embedded font. These are sample technical checks, not validation of every character, dialect or translation.
- Chinese: sample visually readable in this local viewer. Current STSong-Light CID font is referenced rather than embedded; cross-viewer portability remains unverified. Traditional Chinese and all uncommon characters are not established by this sample.
- Korean: confirmed display failure; Hangul is routed to the Chinese CID font and disappears in the rendered sample.
- Hindi: confirmed display failure; 26 distinct sample Devanagari characters absent from bundled DejaVu Sans, producing boxes. Indic shaping also not configured.
- Arabic: sample glyphs exist, but joined letter shaping and right-to-left layout are not configured; rendered sample visibly unsuitable. Character coverage alone is insufficient.

Recommended remediation: bundled licensed fonts for Korean/Devanagari, a renderer with validated complex-script shaping and bidirectional layout, and cross-viewer plus native-reader checks before claiming reliable bilingual PDF support for these scripts. Keep originals available independently of PDF rendering. Do not claim all 12 languages have validated PDF support.

Artifacts: docs/review/language_pdf_audit/results.json, one sample PDF per language and rendered PNGs for the six highlighted scripts. Reproduce with PYTHONPATH=. python scripts/audit_language_pdfs.py in the app environment. No application source changes, merge or deployment performed by this audit.
