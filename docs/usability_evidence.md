# PathwayAI formative usability evidence

This log separates external tester reports, implementation responses and local checks. It is not a clinical study, representative survey, validated language assessment or evidence of savings. No new participants, denominators, timed results or affiliations are inferred.

| Task / observation | Evidence supplied | Response / status | Next confirmation |
| --- | --- | --- | --- |
| Enter care and travel spending; download record | Tester reported correct USD 225 total and requested fields in PDF | Existing calculation retained | Repeat with unknown values and explicit reporting period |
| Include a dated observation | Tester reported full October 15 observation, with 4 caregiver hours separate from overall 8 hours and a double-counting warning | Separate periods and no automatic sum retained | Check whether participants understand the distinction without prompting |
| Navigate to Community and back; edit another field | Tester reported retained amounts and observation | Retention behavior preserved | Repeat across devices; session persistence is not permanent storage |
| Download Russian notes | Tester reported boxes in PDF despite correct app text | Unicode font loading strengthened; local embedded-font, text-extraction and visual checks passed | Original tester's retest not yet received |
| Identify cost-summary period | Tester found overall period 'Not reported' while observation covered past 7 days | Cost period highlighted; explicit seven-day option; no automatic adoption of observation period | Ask whether distinction is clear |
| Scan a shorter report | Tester requested a compact PDF | Optional compact layout for visit, bilingual and cost reports; missing fields omitted while originals, zeros and negative findings preserved | Ask patient/caregiver and clinician which layout is more useful |

Next small review: ask a patient/caregiver whether they can find and download a useful record; ask a clinician whether it preserves relevant information; ask an assistance organization what is required for a support conversation. Record task, completion, assistance, issue, change and retest separately. Use made-up health information until a governed real-data pilot is ready.
