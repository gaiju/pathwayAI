# PathwayAI

Make the invisible burden visible: money paid for care, time away from work,
unpaid caregiving and barriers to support. This pilot website serves people
preparing for care and community teams exploring support priorities.

## Run

Use the existing checkout. Install the repository's requirements and run the
lowercase entrypoint:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m unittest discover -s tests -v
```

`APP.py` is an older entrypoint and is not the current test version. Deploy the
whole branch, including the new Python modules and national boundary file,
rather than uploading `app.py` alone.

## What works now

- Uninsured-care and medical-bill guidance is available before story entry,
  with HRSA health-center lookup, coverage resources, financial-assistance
  questions and a downloadable call checklist. Fees and assistance vary.
- Community action briefs include capacity, staffing and funding checks;
  identifying a need does not create a funded service.
- Optional benefits-conversation checklists reuse selected personal-record facts;
  they do not submit applications or determine eligibility.
- Central evidence scope notes show study counts, populations, periods and limits.
- Short-and-simple or more-detailed reading views.
- Outdoor planning and county context at the ZIP lookup point.
- Visit preparation, optional local story organization and burden recording.
- Reviewed, downloadable visit and cost/time summaries.
- Lyme testing preparation, report vocabulary and cost-estimate questions.
- Sourced public-data comparisons and illustrative scenario exports.
- A map-first Community page with comparisons, planning options and cost evidence.
- Private reuse of earlier patient cost/time entries, without repeat questions.
- Optional public evidence Q&A and an admin-only Research & Strategy Agent.

## What is not established

This is not a diagnostic service, a validated local cost model, a live lab-price
service, or a production-ready county patient-reporting system. Real public
collection is off by default. The fictional demonstration reads no patient
files, sends no data to AI and writes no shared records. Clinical benefit,
savings, adoption and county partnerships have not been demonstrated.

## Secrets and privacy

Existing configuration remains in Streamlit secrets or environment variables.
Never commit secret files, patient reports, raw stories, or credentials. External
story AI remains opt-in with local fallback. Admin access and request limits
remain in place. Keep `PATHWAYAI_PATIENT_VOICE_STORAGE_ENABLED` off until a
reviewed collection pilot is ready; local CSV storage is not a production
security or privacy guarantee. `store=False` does not guarantee zero provider
retention.

## Evidence and demonstration

See [Methods and data dictionary](METHODS.md), [Release report](RELEASE_REPORT.md),
[Presentation walkthrough](DEMO_WALKTHROUGH.md), [RAG evidence](RAG_EVIDENCE.md),
and [County geography](COUNTY_GEOGRAPHY.md).

Source values inherited from the application require source-table verification.
Historical survey comparisons are kept in the bottom detail section and are
excluded from headline results and the public AI evidence bundle.
