# Homepage sample outputs — review branch

Added “See what you can take away” after the existing pathway buttons: one clear patient/caregiver output and one community output, each with a downloadable sample PDF. Existing routes and hero layout are preserved. County description now reflects seven Mid-Hudson brief coverage. A collapsed “Improved through feedback” section summarizes documented saved-record checks, multilingual tester contributions and county-report readability improvements. Testing is not presented as clinical validation, savings or part of the original submitted MVP.

Sample generation uses the existing fictional visit-summary text, a clearly illustrative $225 spending example with workdays/caregiver hours kept separate, and the existing Dutchess county report builder. No AI service, patient inputs or session records are read or copied into samples. Static sample generation is cached in memory. Existing personal PDF and county PDF utilities are reused without changing them.

Validation: Python compilation; focused Streamlit test (homepage samples, no burden-session record, preserved county route and seven options); desktop 1440px/mobile 390px browser checks, no horizontal overflow/UI exceptions; both sample PDFs downloaded through browser; patient route checked. PDF inspection confirms fictional label and $225 total, and four-page county report with references last. No full-suite rerun or live deployment verification for this focused presentation update. No merge/deployment.

Changed source: app.py, homepage_outputs.py. Test: tests/test_homepage_outputs.py. Review samples: docs/review/homepage_samples/. Screenshots: docs/review/homepage_outputs_1440.png and homepage_outputs_390.png.
