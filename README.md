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

The only application entrypoint is lowercase `app.py`. The old uppercase
entrypoint was removed to prevent filename collisions when extracting the
project on case-insensitive filesystems (common on macOS and Windows).
Download a fresh ZIP into an empty folder rather than extracting over an old
copy. Deploy the whole branch, including Python modules and data assets,
rather than uploading `app.py` alone.

## What works now

- Care & Support starts with timely evaluation and tick-bite prevention advice,
  followed by insurance/bill help and then optional story preparation. An
  optional explanation distinguishes localized and disseminated Lyme and cost
  context without predicting an individual bill.
- Uninsured-care and medical-bill guidance is available before story entry,
  with HRSA health-center lookup, coverage resources, financial-assistance
  questions and a downloadable call checklist. Fees and assistance vary.
- Community action briefs include capacity, staffing and funding checks;
  identifying a need does not create a funded service.
- SSI/SSDI preparation explains the adult disability-duration standard and offers
  a functional-history prompt. Short-term missed-work/caregiver totals are not
  automatically inserted as disability evidence. SNAP preparation stays separate.
- Both Tick Bite and Care & Support offer the same notes organizer. Patients can
  choose a writing language and explicitly opt into external-AI English translation.
  Original notes and a reviewable English timeline can be downloaded together;
  notes and results are reused between these pages without another request.
  This is not a fully translated interface or qualified medical interpretation.
- English visit summaries put the exposure-to-care timeline before the original
  notes. Source excerpts preserve reported positive/negative tests and relative
  timing; editable fields allow correction of missing/ambiguous information.
- Payment-help summaries optionally include one bill's organization, date, total,
  amount paid, balance and assistance status, separate from spending totals.
- Central evidence scope notes show study counts, populations, periods and limits.
- Short-and-simple or more-detailed reading views.
- Outdoor planning and county context at the ZIP lookup point.
- Visit preparation, optional local story organization and burden recording.
- Organizing a story immediately shows an editable visit summary and its TXT
  download before testing guidance or cost forms. Editing the original story
  requires organizing it again before a summary is marked ready.
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


## Citing and reproducing the burden evidence framework

The Community Burden & Action page includes a **U.S. burden** tab with historical published national illustrations, a six-domain impact inventory, and separate medical-spending and functional-impact references. It does not calculate a current U.S. total, global total, or Lyme-attributable county disability count. Patient session entries are excluded from the public evidence exports.

- Methods: [docs/burden_methodology.md](docs/burden_methodology.md)
- Machine-readable citation: [CITATION.cff](CITATION.cff)
- Evidence package: [submission/PathwayAI_US_Burden_Evidence_v0.1.0.json](submission/PathwayAI_US_Burden_Evidence_v0.1.0.json)
- Reproduce JSON with `burden_framework.evidence_package()` and the methods brief with `burden_framework.methods_text()`.
- Cite original studies for their findings. The PathwayAI citation identifies a software/methods version, not a peer-reviewed economic estimate or registered DOI.
- Versioned source snapshot: https://github.com/gaiju/pathwayAI/tree/burden-evidence-v0.1.0

National reference values retain original source dollar years and assumptions. International comparison resources are discovery links, not verified global numerical inputs.
