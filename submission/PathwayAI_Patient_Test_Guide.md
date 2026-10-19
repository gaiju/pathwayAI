# PathwayAI: simple patient test guide

Everything below is fictional. Do not enter real names, dates of birth, addresses, Social Security numbers, account numbers or identity documents. This guide describes the main app, not the separate uploaded self-check prototype.

You can read care, bill and transport resources without entering a story. No one needs to complete every field. Optional fields can stay blank. "Not reported" is different from zero. Entries last during this app session; download a copy you want to keep.

## Try the short path first

1. Open https://pathwayai.streamlit.app/ and choose **Quick and easy**.
2. Select **Prepare for care**.
3. Keep **Who is completing this record? → Myself** and **Language → English**.
4. In **Your notes**, paste the fictional notes below. Leave optional AI off.
5. Select **Organize My Story**. Review the visit summary, correct it if needed and download it.
6. Open **Review or add costs and time**. Check the example amounts below, choose the period and phase, then review and download the appointment and cost summary.

### Fictional notes to paste

I found a tick in Dutchess County, New York, in June. Two weeks later I developed a rash and fever. My blood test was positive. It took four months to get a diagnosis. In the past 30 days, I paid $180 for medical care and $45 for travel. I missed 3 workdays. My unpaid caregiver spent 8 hours helping me. I need help with medical bills.

### Check or enter these amounts

| Field | Fictional answer |
|---|---|
| Time covered | Past 30 days |
| When did these costs happen? | Both before and after diagnosis |
| Money paid for care | $180 |
| Other money paid | $45 |
| Workdays missed | 3 |
| Unpaid caregiver hours | 8 |
| Value per missed workday | Leave blank; optional |
| Main barrier | Cost / insurance coverage |
| Question for clinician | What follow-up is appropriate, and which original test reports should I bring? |

The visit summary should retain the positive test as **patient-reported**, the two-week symptom timing and the four-month diagnosis delay separately. It is not an interpretation of the laboratory report. The cost record should show **$225 paid, 3 workdays and 8 caregiver hours separately**. It must not add county estimates to this record or turn the hours into dollars.

## What patients can enter in the short care path

| Group | Fields | Needed? |
|---|---|---|
| Reading choice | Quick and easy / More detail | Default is Quick and easy; switch any time |
| Reporting person | Myself, Myself with help, or caregiver | Has a default; change if appropriate |
| Language | Preferred writing language | English default; other languages available |
| Notes | Place/date, symptoms/onset, tick/rash, tests/results/treatment, help needed | Only needed to create a visit summary; answer what you know |
| AI | Optional English organizer; separate permission for external translation | Not needed for basic English organization; never automatic |
| Tick details | When found, exposure location, current care location | Optional; county/state or ZIP, no street address |
| Money and time | Reporting period, before/after diagnosis, care paid, other paid, workdays, caregiver hours, optional workday value | Only enter the measures you want in the record |
| Barrier | Main difficulty getting care or support | Optional |
| Daily life | Activities that are harder; caregiver's own experience | Optional; keep caregiver and patient experiences separate |
| Clinician question | One question to bring to the visit | Optional |
| Review | Correct generated visit and cost summaries | Review before downloading or sharing |
| Support request | Type of help needed; generated request and support-summary edits | Optional; not an application or booked service |
| One bill | Organization, approximate date, bill total, amount paid, stated balance, assistance status | Optional; no account numbers; not added again to paid totals |
| Benefits preparation | Program, optional functional history for disability programs | Optional; does not establish eligibility |
| Sharing choices | Whether to include the visit summary and relevant cost/function details in a support download | Optional, explicit choices |
| Community Voice | Optional aggregate fields and consent | Collection currently off; not needed for any personal download |

### Optional bill example

Choose **Paying for care** under the help options. Open the support summary and the one-bill section:

- Organization: Example Clinic (fictional)
- Approximate bill date: September 2026
- Total: $600
- Paid toward this bill: $180
- Unpaid balance: $420
- Assistance status: Not yet applied

The support summary should show $420 as an unpaid balance. Do not add $420 to the $225 already paid. Leave the bill fields blank if testing only the visit summary.

### Optional daily-life example

Select **Reading, screens or concentration** and **Work or school**. A caregiver can write: "I spent eight unpaid hours helping with travel and appointment notes during this period." This is an invented example, not evidence about an actual patient.

### Optional language example

Choose **中文 / Chinese** and enter:

六月在纽约州 Dutchess County 发现蜱虫。两周后出现皮疹和发烧。血检结果是阳性。我想整理这些信息，带去看医生。

Read the permission notice first. External AI translation needs consent and configured API access. Review the original and English together; do not treat a plausible translation as verified. When translation is unavailable, the original-notes download remains useful. These screens do not translate every app page or replace a qualified medical interpreter.

## Extra fields in the optional detailed journey form

The detailed form is for people who want more questions. It is not needed for the short-path reports.

- Daily life: discussion areas, changes and support needed, appointment questions.
- Location: current ZIP/county, possible exposure place, month.
- Personal context: age (not date of birth), relevant immune condition.
- Exposure: tick bite, approximate attachment duration.
- Symptoms: rash, fever, tiredness, headache, muscle/joint pain; duration described in notes.
- Testing: whether tested, test type, reported result, timing relative to symptoms, another clinical opinion.
- Function: effect on daily activity and work/school, missed days.
- Journey: time to diagnosis, clinicians seen, prediagnosis visits, travel distance and travel outside the county/state.
- Support: overall paid-spending band, insurance/cost barriers, support areas wanted.
- Detailed burden: period and phase; healthcare payment, specialist and repeat-test components, transport/lodging, other self-paid products/supplies, caregiver hours and work effect, time arranging care, optional income-loss band and daily work value. Follow the on-screen instructions about overlapping payments; do not count specialist/test payments twice.
- Review and sharing: edits to summaries, optional structured themes, county for aggregation and consent when collection is enabled.

## Reports available from these test tasks

1. Visit summary, reviewed exposure and care timeline.
2. Appointment and cost summary, with payments and time.
3. Money-and-time image, when values are entered.
4. Support request, based on the selected need.
5. Support summary, with the bill and visit details you choose to include.
6. Benefits preparation checklist, when you open that tool.
7. Uninsured-care and medical-bill questions, without entering a story.
8. Original notes or reviewed bilingual summary, depending on language and consent.

These are distinct outputs; you do not need all eight. Community briefs and Medicare comparison CSVs are separate planner outputs, not patient reports.

## What to check

Can you find the task? Does the summary preserve your entries? Can you correct it? Can you download it? Are the next steps practical? Does switching to More detail and back preserve the notes and amounts? Test downloads before closing the session.

A fictional example was exercised in the app after these changes. The $225 payment total, separate workdays/caregiver hours, positive-test wording, timeline and preservation across reading modes passed. This is a software check, not a clinical or patient-outcome validation.
