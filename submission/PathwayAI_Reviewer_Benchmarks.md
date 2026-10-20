# Reviewer benchmarks and development priorities

Reviewer-supplied resources:
- CDC medical-content benchmark: https://www.cdc.gov/ticks/communication-resources/tick-bite-bot-1.html
- PatientsLikeMe functional benchmark: https://www.patientslikeme.com/
- MyChart records benchmark: https://www.mychart.org/l/en-us/explore/

These are suggested benchmarks, not partners, endorsements, integrations or sources of patient data. The pages could not be fetched from the development environment during this update; their current behavior and policies have not been independently reviewed. The reviewer's commercial-sharing characterization is not treated as a verified policy finding.

Prioritize clear Lyme education, reviewed visit preparation, and records of economic and caregiving burden. Evaluate PatientsLikeMe-style symptom tracking and understandable displays, and MyChart-style timelines and printable records through user testing. Do not copy their data-sharing arrangements or imply MyChart/EHR connectivity.

A CDC Tick Bite Bot link has been added beside bite guidance. This does not implement or validate the CDC algorithm in PathwayAI. Existing medical content still needs appropriate clinical review.

The outdoor plan now has a PDF download with the PathwayAI tagline and general prevention/after-bite guidance. A resolved destination-state outline is included; surveillance maps and selected health conditions are excluded from the download. It uses no AI and does not calculate an individual risk score.

Community analytics and advocacy features remain separate planning tools. Broader collection and deployment should follow data-quality, privacy and outcome evaluation. No existing community feature was removed as part of this focused update.

## Code-based gap review — October 20, 2026

The three supplied URLs were retried; each failed with a proxy tunnel 403. The following is a comparison against the reviewer's descriptions, not an independent inspection of the sites or their policies.

### Highest-priority improvements

1. One primary Care & Support PDF. The reviewed visit timeline in `visit_summary.py` includes exposure, removal, onset, rash, symptoms, tests, diagnosis and care. The separate quick appointment-and-cost card in `app.py` currently starts with the original story and a smaller structured field set; it does not explicitly include all reviewed timeline fields. A future combined report should reuse the reviewed timeline, then selected costs/time, functional effects, clinician questions and support needs. Preserve original notes in an appendix. Keep optional specialist outputs separate; do not remove useful exports before testing.
2. A simpler route through each task: immediate tick information; optional preparation questions; review; one clear next step. The CDC link is present, but that is not implementation or clinical validation of its algorithm. Clinician review is needed before new medical routing rules or risk categories.
3. Repeated burden records with explicit dates and the same reporting period. Current money/time records cover one session and can be downloaded; the app is not a secure longitudinal tracker. Begin by designing a dated downloadable diary with consistent fields and patient/caregiver attribution. Persistent accounts, uploads, reminders or shared trend data require a separate privacy/security design.
4. Keep patient-reported symptom/function changes distinct from clinically verified findings. Do not label a custom severity scale as a validated patient-reported outcome measure. Select and review an appropriate instrument before making validation claims.
5. Keep county planning available as a separate secondary path because this is the Cost of Illness track. Label illustrations, synthetic examples and measured data. Defer expansion of shared analytics or AI advocacy until consent, data quality, governance and evaluation are ready; do not imply county adoption or proven savings.

### Existing strengths to retain

- Education and care resources are accessible without a story.
- Tick and care pages share notes within a session.
- Reviewed timeline preserves patient-reported results and separates onset from diagnosis delay.
- Cost periods are explicit; paid dollars, missed days and caregiving hours remain separate.
- Caregiver observations and the caregiver's own experience have separate labels.
- External organization/translation is optional, with review and privacy notices.
- Reports are downloadable PDFs; CSVs remain clean tables.

### How to assess improvements

Ask reviewers to use fictional cases. Measure completion time and assistance needed; verify that positive/negative results, dates, amounts and original wording are preserved; check whether they can find the correct care resource and download a readable report. These measures establish usability and report fidelity, not clinical benefit or cost savings.
