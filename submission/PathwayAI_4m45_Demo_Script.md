# PathwayAI: 4-minute-45-second live demo

Reviewed October 17, 2026. Code: f8488b31877b008d6f0131a3482f635566ec858b. Main and rag-test match. Local Streamlit AppTest walkthrough and 45 tests passed; live Streamlit deployment was not inspected. No application code changed.

## Before you present

Use https://pathwayai.streamlit.app/. Start a fresh session and choose Short and simple. Keep optional external AI off. Have this fictional story ready to paste. Keep download settings from opening another application. Rehearse the scroll positions; the Community page is long. For a short jump, browser Find can locate “Build a community discussion brief”; close Find before interacting.

## Fictional story

I felt tired after an outdoor walk and need help preparing for a visit. I paid $180 for medical care and $45 for travel. I missed 3 workdays. My unpaid caregiver spent 8 hours.

## 0:00–0:20 | Open on the title slide

**Do:** Keep the title slide visible; then switch to the app start page.

**Say:**

I’m Yuwei Zhang from Team GreenAcorn. PathwayAI connects the personal care journey with community burden planning. I’ll show three working outputs: an organized story, a cost-and-time card, and a community planning brief.

## 0:20–1:25 | Organize a story

**Do:** Click “I need care & support.” Leave “Who is completing this record?” at “Myself.” Paste the fictional story below into “Your story, in your own words.” Keep “Use external AI to organize my story” off. Click “✨ Organize My Story.” Open “Review or add costs and time” if needed; choose “Past 30 days” under “Time covered by these entries.”

**Say:**

People who feel tired, dizzy or have trouble remembering details may struggle to prepare for care. Here, they can write a short story instead of entering the same information repeatedly.

This fictional person paid 180 dollars for care and 45 dollars for travel, missed three workdays, and received eight hours of unpaid help.

I click Organize My Story. Clearly stated values appear in fields the person can check, change or clear. I’m using local rules; the optional AI organizer is not required.

## 1:25–2:15 | Review the card and downloads

**Do:** Scroll to “Review and download your visit and burden card.” Show the money-and-time image and editable summary. Click “Download appointment and cost summary.” Point to “Download my money-and-time image”; do not open a separate application during the timed demo.

**Say:**

The card brings the story, costs and questions together. Payments total 225 dollars. Missed work stays in days and unpaid help stays in hours; I have not assigned either a dollar value.

The summary can be corrected and downloaded for visits with different providers. There is also a separate downloadable image.

Caregiver reporting is available, with observations and the caregiver’s own experience labeled separately. These are personal records, not diagnoses or verified clinical assessments.

## 2:15–3:10 | Show community evidence

**Do:** Click “Explore community burden →.” Keep the default “Reported Lyme rate.” Briefly show “Compare Dutchess and Orange counties,” then scroll to “Estimated community cost: Dutchess and Orange.”

**Say:**

Now we move to community planning. The Hudson Valley pilot view compares Dutchess and Orange using reported Lyme rates, trends and cost illustrations.

The combined societal illustration is about 4.11 million dollars in 2016 dollars: reported 2024 cases multiplied by a published study mean. Medical costs are shown separately from other expenses and lost productivity.

This illustrates scale. It is not measured county spending, and it does not add this person’s card to the county totals.

## 3:10–4:05 | Build and download the community brief

**Do:** Scroll to “Community action.” Expand “Build a community discussion brief.” Under “Choose a focus for the brief,” select “Reaching care.” Show Focus / Action / Track, then click “Download community planning brief,” immediately below the calculator panels. Leave those calculators and the AI panel closed.

**Say:**

The next question is what a community team could do with this information.

I select Reaching care. The app suggests reviewing transport, cost and communication barriers, and tracking reported barriers, completed referrals and appointments attended.

The downloadable planning brief brings that focus, a proposed next step, measures and evidence references together. It is a starting point for discussion, not an adopted county program or proof that support was delivered.

## 4:05–4:45 | Return to the title and close

**Do:** Return to the title slide with the app link and QR code. Finish by 4:45.

**Say:**

Community feedback showed us that costs extend beyond bills to lost work, food, housing and maintaining benefits. The MVP now helps people prepare requests for that support.

The next phase is secure, consent-based local reporting to understand costs and barriers that routine data may miss. Biobank follow-up findings provide symptom context, not delayed-diagnosis costs.

We are seeking patient, caregiver and community partners to test usefulness and improve the evidence. Health benefits and savings remain to be evaluated. Our goal is timely care and less disruption to work and family life. Thank you.

## Verified download labels and formats

- Download appointment and cost summary → PathwayAI_AppointmentSummary.txt
- Download my money-and-time image → PathwayAI_MoneyAndTime.svg
- Download community planning brief → Community_BurdenBrief.txt

## Review findings that affect the demo

1. The personal download is TXT, not PDF; the visual is a separate SVG. Do not promise a combined PDF or persistent account history.
2. The community brief contains additional published references and scenario assumptions, including a note that original Yu cost tables await verification. Do not call the whole brief independently verified local evidence. The primary on-screen Hook-based societal illustration is distinct.
3. Changes to the free-text summary do not automatically recalculate the visual. Change amounts in their number fields if needed; for this demo keep the tested values.
4. Caregiver-on-behalf stories do not automatically prefill patient cost fields. Keep the demo reporter at Myself and mention the caregiver option without switching roles.
5. Patient entries remain in the session and downloads; they do not automatically contribute to county totals.

## Working now versus future

Working: local story organization, explicit-value prefilling, reviewed TXT summary, SVG visual, labeled caregiver records, support resources and requests, basic benefits-preparation checklist, county comparisons and planning-brief download.

Future: secure consent-based reporting pilot, representative local cost estimates, verified medication prices, validated symptom/functional measures, automated benefits submission, demonstrated outcomes or savings. The basic benefits checklist already works; it is not an eligibility assessment or application service.

## Timing fallback

If a live action takes more than 10 seconds, say “I’ll use the saved fictional example to keep us on time.” Show the saved card or brief transparently as a backup. Begin the Community section by 2:15 and the brief by 3:10. Skip extra charts, detailed forms, AI evidence questions and benefits examples. Keep the closing at 4:05.

## Optional answers after the demo

**What is the evidence sample size?** Hook’s societal analysis has 613 participants, distinct from its 901-person patient analysis. The Biobank has 253 returners out of 466 enrolled cases; selected returners do not establish county delayed-diagnosis burden. The small survey snapshot has unresolved question-level denominators.

**Does this prove savings?** No. The model illustrates scale; pilot outcomes require evaluation.

**Does the brief include the story I just entered?** The public planning brief did not contain the fictional story in the tested workflow. Personal data remain separate.

**Where are the sources?** In the brief and the sidebar’s Sources & Acknowledgements page.
