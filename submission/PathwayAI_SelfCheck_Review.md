# Uploaded self-check review

Reviewed the supplied PathwayAI_SelfCheck.zip README, rule code, optional AI/photo workflow, tests and preview. No uploaded launch scripts or network calls were executed. The package has not been integrated or deployed.

Useful design ideas: structured exposure/tick/rash/symptom questions, Not sure options, a temporal clinician summary and understandable visuals. The preview is still a long single page and may overwhelm users with fatigue or cognitive difficulty. Use a small number of questions at a time, with optional extra detail. Label examples as fictional and keep them separate from real inputs.

Important before public use:

- Sudden facial weakness/drooping must not receive a generic same-day-clinician recommendation without stroke emergency screening. The supplied rule groups it under TODAY. A new sudden focal neurological symptom can be a stroke and requires emergency action. Do not assume Lyme is the cause.
- The rules offer appointment timing and prevention eligibility cues. Software tests and a "not diagnostic" disclaimer do not establish clinical validation or regulatory status. Have a qualified clinician review every branch against current guidance; keep suspected infection/treatment decisions with clinicians.
- The claim that AI never influences a decision is overstated. Accepting AI-suggested answers changes the inputs to the rules. AI can misidentify tick species, infer attachment time from appearance or misread a rash. Do not use photo suggestions as a reliable basis for care urgency, prevention eligibility or diagnosis.
- Incomplete forms must not imply a reassuring result. The rule treats unanswered rash differently from explicit Not sure, and the UI requires only two answered questions before showing its result. A watch-only recommendation must not imply illness has been excluded.
- A new photo or changed text must invalidate prior suggestions before reuse. Review identifiers, metadata, upload limits, consent, retention and external-provider handling before any image integration. The prototype is not the proposed test-report redaction feature.
- Some README repository observations are stale: the current app uses lowercase app.py and has already had additional fixes. Do not apply document integration instructions automatically.

Recommendation: retain the short question-and-summary idea; do not publish this medical self-check unchanged. Offer an optional captioned 45–60 second getting-started video for the current app. The app must remain usable without watching it. The separate patient video script describes current organization/navigation features, not unreviewed self-triage or photo analysis.
