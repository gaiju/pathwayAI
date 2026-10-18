# PathwayAI: presenter Q&A and original-proposal scope

Use this document for questions after the demo. It is separate from the clean spoken script. Answers distinguish the original concept, today's working MVP and future research. Office-hours remarks are meeting feedback, not agency endorsement or a formal data-access determination.

## Short answer if a judge asks why the MVP differs from the original

“The original concept explored the cost of delayed and missed diagnosis across Lyme and Long COVID. The working MVP concentrates on Lyme, patient preparation and transparent community-planning evidence. The public data available for this version do not establish individual pre-diagnosis trajectories or causal savings. We kept that research question, but did not present the concept's simulated figures as validated results.”

## 1. What did the CMS speaker actually explain?

“In the October 8 office hours, I asked about studying utilization, costs and disability before and after diagnosis. The CMS speaker explained that their public aggregate files could not answer that specific individual-journey question. Beneficiary-level longitudinal claims would be needed, with appropriate access and methods. Claims also have limited clinical detail and do not represent everyone.”

Source: Office Hours 10_8 transcript, my question at 25:26 and CMS response at 27:00–29:45. The speaker described provider/facility-level aggregation, Medicare/Medicaid population limits, beneficiary identifiers for longitudinal study, VRDC/CCW access and the administrative nature of claims. Do not turn that response into “CMS data are unusable” or “aggregation is forbidden.” Access arrangements and current requirements must be checked through CMS/ResDAC for a specific project. No controlled CMS claims were obtained for this MVP.

## 2. Why not simply aggregate all the available data?

“We can summarize compatible observations, but combining totals cannot reconstruct a person's journey. County surveillance, provider counts, research samples and voluntary patient reports describe different populations, periods and questions. We show them alongside one another with their sources and limits rather than pretend they are linked records.”

Real patient-report aggregation would additionally require consent, secure storage, comparable fields and periods, duplicate handling, missing-data checks and disclosure/statistical review. County of residence is not necessarily exposure location or care location. A small-group threshold alone guarantees neither privacy nor precision.

## 3. Why didn't you deliver the original Bayesian data-bridging model?

“The mockup laid out a research concept. We have not demonstrated the linked longitudinal data, validated transition estimates, causal comparisons or reproducible fitted model needed to support those numerical outputs. The MVP therefore uses inspectable calculations and clearly labeled scenarios while the larger research model remains future work.”

A Bayesian method does not by itself solve missing clinical information, selection bias, incompatible populations or causal identification. Public synthetic data may test software, but cannot establish actual Lyme progression, costs or intervention effects without an independently justified research design.

## 4. What about the numerical results shown in the original mockup?

“They belong to a simulated concept display, not validated findings from the current app. I would not use them as evidence of what PathwayAI has measured or saved.”

In the supplied six-page mockup:

- Page 1 displays 2.2×/3.2× cost multipliers, a 22-month delay, $30,600 saved per patient and more than $1.2 billion in avoidable annual costs. No supporting executable analysis or validated inputs were established in this review.
- Page 2 describes simulated pathways and labels 17,740 patients plus 17,740 controls. Do not present that label as an actual recruited or linked cohort.
- Pages 3–4 display modeled trajectories, uncertainty intervals and matched-control/causal-method labels. No fitted posterior, valid uncertainty calculation or causal effect was verified.
- Page 5 ranks simulated intervention savings and assumes uptake. Do not call those programs proven effective, funded, available or cost-saving.
- Page 6 gives proposed dataset suitability ratings. These are concept judgments, not validated data-quality scores, evidence of access or proof of integration.

Keep the original document as historical design material. If displayed externally, identify these limitations before anyone could mistake the graphics for study results. Do not reintroduce those numbers into the final narration or current evidence outputs.

## 5. Who benefits now: patients or policymakers?

“Both have a practical starting point. Patients can find care-access information, prepare a reviewed visit summary, record costs and time, and download support questions. Community teams can compare public county context and download a planning brief. Whether those outputs improve access or outcomes still needs testing.”

In my October 8 question I described policymakers and local public-health leaders as primary users. The current patient tools give contributors an immediate use for their information and support future community work. Private patient entries are not automatically added to population evidence or county totals.

## 6. How does the family insurance story connect to the actual tool?

“Losing insurance is why I wanted a usable starting point. PathwayAI points uninsured people to HRSA health centers, explains questions about income-based fees, links coverage options, and helps them ask about hospital financial assistance. It does not enroll someone, arrange an appointment, pay bills or guarantee help.”

HRSA-funded health centers serve uninsured patients regardless of immigration status; care is not automatically free. Sliding fees depend on income and family size. Insurance eligibility is a separate question. Services, fees, appointment capacity and assistance must be confirmed directly. Coverage paperwork should not delay asking a clinician about a time-sensitive bite or symptoms.

## 7. Can you say timely support prevents dissemination, disability and costs?

“Early treatment can help prevent Lyme disease from spreading and reduce serious complications. Practical support may help people reach care sooner. Reducing disability, disruption and future costs is our goal; we have not demonstrated those effects for PathwayAI.”

Do not equate localized/disseminated disease categories with measured diagnostic delay, or claim every patient progresses through the same stages. A tick bite does not always cause Lyme disease, and antibiotics are not needed after every bite. A clinician assesses preventive treatment after selected high-risk bites; the app does not prescribe it.

## 8. What costs does the app actually measure?

“The personal record holds what someone reports paying, their missed workdays and unpaid caregiver hours for a stated period. Those are reviewable personal entries, not audited expenditure or a complete cost-of-illness estimate. County illustrations use published unit costs and reported cases with explicit assumptions.”

For the fictional demo, $180 care plus $45 travel equals $225 paid; three missed workdays and eight caregiver hours stay separate. Unknowns remain unknown. Clinical records, insurer payments, lost opportunities and nonresponders' burdens are not fully captured. The app does not establish local total pre-diagnosis costs.

## 9. How do you avoid double counting?

“We separate payments, time, study perspectives and dollar years. We do not add a medical-episode estimate to a societal estimate that already includes medical costs, or add patient out-of-pocket again when it is already part of the medical total.”

Hook's societal reference uses 2016 dollars; Yu's medical-episode reference uses 2022 dollars and original-table verification remains pending. The primary county societal illustration uses Hook rather than Yu. Disability benefit payments are transfers, not automatically additional societal resource losses. Work loss and caregiver valuation require checks for overlap and assumptions before combining them. The original mockup's stacked SSA/productivity/OOP categories are not a validated societal accounting model.

## 10. Why not use MEPS or another national dataset for county Lyme costs?

“A dataset must fit the question. Office-hours discussion identified sparse Lyme samples and uncertainty in expenditure surveys. Those data cannot automatically produce reliable county or pre-diagnosis estimates. We retained them as research leads, rather than manufacture a local estimate.”

Sources: September 24 transcript, 31:28–36:05 on sparse samples and expenditure variability; 39:33–41:19 on geography/purpose. October 15 chat, 00:53:50–00:54:17 distinguishes NHIS health context, MEPS expenditures, ATUS time-use and ACS local context. No new numerical MEPS, ATUS, HCUP, All of Us, RECOVER or CURE ID findings were incorporated on that basis. Do not claim the original cross-dataset linking was implemented.

## 11. What is the AI contribution?

“Optional AI helps organize a person's words for review and explain curated public evidence. Cost arithmetic is deterministic. Private patient cards are not used by the public evidence assistant. The basic organizer also works without external AI.”

External story assistance is opt-in; users should omit identifiers. AI does not diagnose, confirm a disease trajectory, determine benefits eligibility or validate a cost model. Translation, certified medical interpretation and health-system integration are not established features.

## 12. A gap may exist because there is no money. Then what?

“That is why the brief asks about capacity, staff, costs, responsibility and a possible funding source. It can help partners prepare a budget discussion or philanthropic proposal, but it does not create funding. If no service is available, that remains an unmet need.”

No county adoption, duty to fund, partner commitment, funded referral or guaranteed service is established. Evaluate existing services before proposing a new one; a list of clinics is not evidence of open appointments, affordable testing or successful referrals.

## 13. What did patient and advocate feedback change?

“It broadened the design beyond bills: unpaid care, daily tasks, missed work, isolation, food, housing and difficulty reaching support. It also reinforced the need for short forms, reviewed summaries and clearly attributed caregiver observations.”

Sources: October 15 transcript 14:11–24:49 and 33:49–40:37; October 15 chat 00:43:42 on organizing evidence for benefits conversations and 00:57:37 on stylized examples of lost opportunities. These comments inform design; they do not constitute a completed usability study or clinical validation. Severe illness can make participation difficult, but do not claim all national surveys exclude proxy respondents: the October 15 chat at 00:59:32 explicitly notes family respondents in MEPS/NHIS.

## 14. How do you know the tool works?

“Technical checks cover navigation, calculations, downloads and preserving entries. We have incorporated feedback, but have not established clinical effectiveness or measured community impact. Next, we need a consented pilot with patients, caregivers and willing service partners.”

Useful pilot measures: usability and accessibility, summary correction burden, whether a referral reaches a service, appointments attended, financial-assistance outcomes, unmet needs and comparable spending/time records. Predefine reporting periods, denominators, missingness and follow-up. Before/after changes alone do not prove causal savings. A comparator and appropriate clinical/economic study design would be needed for stronger claims.

## 15. What are the main remaining gaps?

“Secure shared reporting, durable records over time, validated local pre-diagnosis estimates, dependable service availability, partner funding and measured outcomes. These are the next research and delivery steps, not completed capabilities.”

Specific needs: controlled-data permissions where relevant; data-use, privacy and retention review; accessible participation and authorized caregiver arrangements; duplicate handling; comparable time/geographic definitions; source-table verification; an outcome evaluation design; and named partners with feasible responsibilities. Current shared collection is off. A prototype's local file store is not a production privacy guarantee. Downloads are TXT/SVG, not FHIR integration or automatic exchange between clinicians.

## 16. Why Lyme first rather than both Lyme and Long COVID?

“The original vision was broader. This MVP focuses on a concrete Lyme use case and local county comparison. Extending the structure to other illnesses would require condition-specific evidence, clinical review, user testing and data governance. We cannot assume Lyme pathways or costs transfer to Long COVID.”

## Positioning and presentation reminders

- The entrant has confirmed the category: **TOPx HHS | Cost of Illness**. The original mockup also labels the Cost of Illness track. Lyme is the MVP use case; this does not make the accepted category Lyme Innovation. The final video must emphasize human/economic burden, open-data evidence and practical uses. The current official scoring rules have not been independently reverified.
- The entrant supplied the official track listing: **PathwayAI: Full Economic Burden — GreenAcorn**, **Cost of Illness Track**. Use that registered project title, with **Making the Hidden Patient Journey Visible** as the presentation subtitle. Yuwei Zhang can introduce herself without the team name. The historical mockup's longer network heading describes its earlier concept. “Full” is the ambition, not a claim that the MVP already measures every cost.
- No NIH/CMS name is needed in the spoken introduction. Discuss the CMS response only if asked about data access, model scope or feasibility. Do not imply endorsement.
- Final narration contains no slide or pause markers. The benefits-only scene remains omitted; care-access and hospital financial-assistance guidance remain included.
- Readable explanation of the scope decision: **“We kept the question, narrowed the implementation, and made the limits visible.”**

## Source record reviewed

- User-supplied `mockup.pdf`, six image-only pages: rendered and visually reviewed page by page. It is a prototype concept with simulated labels, not a verified results report.
- October 8 office-hours transcript, 25:26–29:45: PathwayAI question and CMS response, re-read directly.
- Saved September 3, September 24 and October 15 transcript/chat mapping: `Office_Hours_Feedback_Implementation.md`; underlying October 15 chat was also checked for the quoted timestamps.
- Repository implementation and submission notes, including current care-access guidance and the working-versus-future distinctions. Formal rubric changes and current external data-access requirements were not independently verified in this workspace.

## 17. Has the external public-health review been fully addressed?

“Partly. We made the pilot website and audience explicit, removed the public reviewer walkthrough, added care-access guidance and made existing transport contacts accessible without a story. But a referral directory does not create appointments, transport capacity or funding. We still need users and service partners to test whether the proposed next steps are useful.”

Gray source notes and safeguards are supporting information, not unfilled copy placeholders. A full public-facing readability/accessibility review remains appropriate. Proposed outreach is through willing patient groups, health centers, navigators and community organizations; no distribution agreement, county adoption or endorsement is established.

## 18. Can we claim $1,944 saved for every earlier Lyme diagnosis?

“No. Hook reports mean societal costs of $1,307 for confirmed localized and $3,251 for confirmed disseminated cases, in 2016 dollars. Their $1,944 difference is an observational comparison between clinical groups. It is not an estimated causal saving from an earlier diagnosis or an effect of PathwayAI.”

Clinical extent is not interchangeable with diagnostic delay. Groups can differ in severity, care needs and other factors. Do not multiply $1,944 by users or earlier appointments and label it achieved or expected savings. It can motivate an evaluation question, with appropriate design and explicit assumptions. The repository's bounded Hook summary already makes this distinction; no new savings calculation is added.

## 19. Why not add photo recognition or Apple Health before the demo?

“Those are research directions, not validated capabilities in this MVP. We can demonstrate the working, reviewed visit summary now. Images alone cannot establish tick attachment time, Lyme disease or whether preventive antibiotics are appropriate. Wearable measurements are nonspecific and do not diagnose Lyme.”

A future image workflow would need clinical review, appropriate validation, uncertainty handling, consent and secure image processing. Calling a feature a risk alert rather than diagnosis does not by itself determine its regulatory status. A browser-only app does not directly read HealthKit; an authorized native integration or separately designed import workflow would be required. Activity or sleep records could support future functional-burden research, with careful attention to baseline, missingness and alternative explanations, rather than automatic causal attribution.
