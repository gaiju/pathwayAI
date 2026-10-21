# PathwayAI: 20-minute Q&A practice guide

15 practice blocks × 80 seconds = 20 minutes. For each block: question (10 seconds), core answer (up to 40 seconds), follow-up discussion (30 seconds). This is an allocated rehearsal, not a claim that reading the answers alone lasts 20 minutes. Use only documented results; fictional and proposed work remain labeled.

## 1. What have you actually delivered?

PathwayAI is a working pilot web app with prevention information, an outdoor plan, visit preparation, optional AI-assisted English summaries, expense and time records, care-access resources, and public-data planning views. Users can review and download outputs. It does not diagnose illness, enroll people in benefits, or establish that a county has adopted a program.

**Follow-up: What should you demonstrate?**
Open one reviewed visit summary, one cost record, and one planning brief. Distinguish a working feature from a proposed pilot. Do not describe a mockup as an implemented model.

## 2. Who is the main user, and who benefits?

Our intended organizational users are county health departments and community partners. Patients and caregivers are the direct users of preparation and support tools. Residents and outdoor visitors can use prevention information. We are seeking pilot partners; intended users are not the same as established customers. Patient needs should shape what a community pilot measures.

**Follow-up: Why serve both audiences?**
A useful patient tool provides immediate preparation. A separate community view helps frame resource questions. Future connections require consent and governance, not automatic sharing.

## 3. What practical benefit does a patient get?

A patient can prepare a clearer account of exposure, symptoms, test results, and care, then review and download it. Early Lyme disease can often be managed in primary care, but each center must confirm evaluation, treatment or referral, appointment timing, interpreter access, and fees. They can find questions about uninsured care and financial assistance and keep expenses, missed work, and unpaid help together. We have not established that these tools shorten diagnosis or improve treatment outcomes. The first evaluation should test accuracy, ease of use, and usefulness in support conversations.

**Follow-up: What would count as success?**
Define tasks before testing: complete the summary, identify a care resource, download the correct report, and report whether it helped a conversation. Record mistakes and unsuccessful attempts as well as successes.

## 4. Does this meet the full economic burden challenge?

It addresses dimensions that a medical bill alone misses: nonmedical expenses, time away from work, and unpaid caregiving. Published societal costs add context. We do not claim a validated estimate of every cost or the lifetime population burden. Long-term symptoms, undiagnosed illness, and people missing from existing datasets remain important gaps. The pilot makes several dimensions measurable and identifies what stronger evidence is needed.

**Follow-up: Why not monetize everything?**
Monetizing time requires a valuation rule and observation period. Workdays and caregiving hours are useful measures without pretending they can be added directly to dollars. Any later monetary conversion should be explicit and checked for double counting.

## 5. Where do the $2.15 million and $1.96 million figures come from?

NYSDOH reported 1,060 Dutchess cases and 964 Orange cases in 2024. We multiply each count by Hook’s mean societal cost of $2,032 per participant in 2016 dollars. The exact products are $2,153,920 and $1,958,848. These are study-based illustrations, not observed county spending. The assumption is that the published average is informative for reported county cases, despite differences in population, case mix, and prices.

**Follow-up: What is included, and what about inflation?**
The benchmark includes medical, nonmedical, and productivity costs within the study scope. Current illustrations retain 2016 dollars without inflation or underreporting adjustment. Do not add the same patient payments or productivity losses again.

## 6. Does earlier treatment save $1,944 per patient?

We cannot make that claim. Hook reported mean societal costs of $1,307 for confirmed localized disease and $3,251 for confirmed disseminated disease, in 2016 dollars. Their difference is $1,944, but the groups were not a randomized comparison of earlier and later treatment. The study supports an observed cost difference, not an intervention savings estimate. CDC guidance separately supports early appropriate treatment to help prevent more severe disease.

**Follow-up: What evidence would establish savings?**
Define the intervention and comparator, measure treatment timing, costs and outcomes over a common period, and address patient differences and missing data. A pilot can first establish feasibility before attempting causal savings estimates.

## 7. What can a county do beyond viewing familiar public data?

The proposed value is bringing sources into a clear planning workflow: a defined need, a possible response, potential partners, and evaluation measures. For example, a navigation pilot could connect uninsured residents with existing clinics and language or financial-assistance resources. It needs confirmed service capacity, staffing, and resources. A dashboard cannot solve a funding shortage or create appointments by itself.

**Follow-up: How would you measure community usefulness?**
Ask county reviewers whether the brief changes or clarifies a decision, identifies a feasible partner action, and supports a defined evaluation. Track unresolved barriers rather than counting every referral as a successful connection.

## 8. Where does AI do meaningful work?

With explicit permission, optional external AI helps organize and translate a user’s narrative into an English summary for review alongside the original. This is a communication task, not diagnosis. Calculations remain deterministic. The English organizer and resources also work without external AI. Evidence lookup should be described according to its actual implementation; keyword retrieval is not a trained predictive model or proof of a sophisticated RAG system.

**Follow-up: What if the AI call fails?**
Keep the local English organizer, resources, and downloads available. Use a clearly labeled previously generated fictional example if needed. Never present a saved result as a live model response. Check important details against the original.

## 9. How do you protect meaning across languages?

Users can write in their preferred language or mix languages, keeping terms and place names in English. Optional AI prepares English text alongside the original for review. We have invited Mandarin-, Spanish-, and English-speaking reviewers; that is ongoing usability work, not completed translation validation. The app is not a fully translated interface and does not replace a qualified medical interpreter.

**Follow-up: What should multilingual reviewers check?**
Check whether positive versus negative results, dates, uncertainty, medication names, and place names survive correctly. Record omissions and mistranslations. For clinical conversations, encourage a qualified interpreter rather than relying on an unreviewed AI translation.

## 10. Why not use Bayesian modeling or propensity-score matching?

Bayesian methods can combine evidence and describe uncertainty, but require a defensible model of how the sources relate and sensitivity to assumptions. Propensity-score methods require comparable patient-level data, relevant confounders, overlap, and outcomes. County aggregates do not supply the needed individual histories. Neither approach automatically repairs missing information or establishes causation. We chose transparent arithmetic for the current pilot.

**Follow-up: What could you build next?**
A labeled sensitivity simulator could vary case counts or assumed disease mix. It would answer hypothetical planning questions, not claim intervention effectiveness. A later research model would need documented assumptions, suitable data, and external validation.

## 11. Why not train a diagnostic or cost-prediction model?

We do not yet have an appropriate, sufficiently representative training and validation dataset with the necessary labels and follow-up. A model could look accurate while missing underserved people or learning differences in access rather than disease. Our immediate AI task is organizing patient-provided information for review. Diagnostic or personalized care functions would require a separate clinical, safety, privacy, and regulatory assessment.

**Follow-up: Are photos and wearable data available now?**
Do not claim they are integrated. They remain possible research directions. A photograph alone should not determine attachment duration, Lyme diagnosis, or preventive treatment. Wearable changes are nonspecific and need clinical context.

## 12. How do you handle privacy and clinical safety?

The demonstration uses fictional information and shared collection is disabled. Notes and outputs are held within the server-side app session. External AI requires an explicit choice and action and sends information to that provider. Clearing a session is not a promise to delete downloaded files or all provider and hosting records. The app explains its educational role and asks users to review outputs and bring original test reports.

**Follow-up: What must happen before broader real-patient reporting?**
Document data flows, access controls, retention, deletion, hosting and provider arrangements, consent, accountable operation, and incident procedures. Avoid blanket HIPAA or zero-retention claims. Reported experiences must remain distinguishable from clinically verified findings.

## 13. Have you tested it, and what does that prove?

People living with Lyme disease and a county health commissioner reviewed the working app. Their feedback informed simpler wording, navigation, and clearer practical next steps. Language-focused invitations and testing are ongoing. These are formative reviews, not a representative clinical study or proof of improved outcomes. Only report completion times, participant counts, language results, or error rates that have actually been documented.

**Follow-up: What can you measure in the next day?**
Use the same fictional task with a few willing reviewers. Record task completion, elapsed time, wrong or missing details, and usefulness feedback. Describe the small sample and do not generalize percentages to all patients.

## 14. Your mockup shows matched patients and large savings. Are those findings?

No. The earlier mockup was a concept visualization with simulated projections. We have not established a linked cohort of 17,740 matched patients or verified the mockup’s cost multipliers and projected savings. Those must not be presented as findings. The working app uses documented public-data context and transparent calculations. We should omit any mockup number that cannot be reproduced from supported sources and explicit assumptions.

**Follow-up: Why did you narrow the scope?**
To deliver useful preparation tools and reviewable evidence while identifying what a larger model requires. Explain that choice candidly. Do not invent a retrospective analysis to justify a number in a concept graphic.

## 15. What happens after the Sprint, and what partnership do you need?

We are seeking willing patient groups, health centers, navigators, and county or community partners for a small pilot. First, agree on a concrete use case, privacy arrangements, responsibilities, and measures. Evaluate summary fidelity, ease of use, support connections, and unresolved needs. Confirm capacity and a costed work plan with partners. Free patient access through grants and partnerships is a proposed sustainability model, not secured funding.

**Follow-up: How much money will it save, and how much do you need?**
There is no validated savings estimate or finalized pilot budget yet. A budget should specify staff time, language review, secure hosting, maintenance, and evaluation. Do not equate societal burden with county budget savings or assume reduced referrals are always better.
