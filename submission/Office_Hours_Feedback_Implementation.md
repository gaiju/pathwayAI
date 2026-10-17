# Office-hours feedback and implementation

Based on four project-lead uploads: `Office Hours 2 Cost of Illness 9_3 Office Hours_otter_ai_transcript (1).pdf`, `9_24 Cross Track Data Office Hours_otter_ai_transcript.pdf`, `Office Hours 10_8_otter_ai_transcript (1).pdf` and `1015.pdf` (Office Hours 10_15). These are meeting transcripts, not independently verified guidance, an endorsement or a formal regulatory determination. October 15 was read using OCR; names and exact wording may contain transcription errors. Additional notes can be added to this mapping.

| Meeting evidence | Application response | Boundary / next step |
| --- | --- | --- |
| Sep 24, 05:41–09:32: preserve source, timing, collection type and modeled-versus-observed status, with accessible metadata. | The pathway now has a source/period/type/scope table, also included in the downloaded action brief and combined county brief. | No invented retrieval date or clinical-record provenance. |
| Sep 24, 13:30–16:44 and 19:36–22:31: longitudinal self-report can be useful; synthetic examples can test software but do not establish clinical outcomes. | The fictional demonstration is explicitly separated from private patient cards, population evidence and real longitudinal records. | No clinical validation, real research-dataset derivation or causal inference is claimed. |
| Sep 24, 31:28–36:05: Lyme samples in MEPS are sparse, treated-prevalence coding misses some burden, and skewed expenditure distributions may make even pooled estimates unstable. | Existing study and survey limits remain; no MEPS Lyme-cost estimate is added. Suppression thresholds are not called statistical reliability guarantees. | Future research needs review of survey design, variability, sample availability and the specific estimand. Transcript sample counts are not reused as current dataset facts. |
| Sep 24, 39:33–41:19: choose the relevant geography and comparison purpose before choosing a dataset. | Each community theme states the planning decision and explains what county context can contribute. | Population context does not determine individual need. |
| Sep 24, 50:21–52:18: data relevance and reliability matter more than assuming a universal real-world-data hierarchy. | Evidence metadata explains scope and collection type without ranking every source by label alone. | This is meeting advice, not a formal FDA determination. |
| Sep 3, 01:08–02:06: federal open data or standards, designing with end users, and a working digital tool are emphasized. | Patient-centered start-page message and a usable county planning pathway with downloadable output; existing public-data integration remains in place. | This implementation is informed by meeting feedback, not a completed co-design study or endorsement. |
| Sep 3, 25:30–33:18: Green Acorn presents PathwayAI; feedback asks for a specific scenario and decision-maker, while supporting attention to pre-diagnosis burden. | Each planning theme now states a decision to explore, including a county care-navigation team considering a small ride-navigation pilot. | No partner decision, clinical inference or modeled pre-diagnosis county cost is claimed. |
| Sep 3, 16:07–18:57: fragmentation and changing needs make a snapshot incomplete. | Community planning asks for repeated check-ins and common reporting periods; existing personal summaries can be reviewed and downloaded. | Durable longitudinal records are not implemented. |
| Sep 3, 48:01–49:51 and 50:16–55:55: clinic presence and distance do not establish usable referrals or accessible transport. | The visible planning section distinguishes clinic counts from accessible appointments, suitable transport and referral quality; transport follow-up includes accessible rides. | No unverified transport availability, clinical statement or prevalence estimate is imported. |
| Oct 8, 25:26–29:45: PathwayAI asks about pre-diagnosis costs and policy usefulness. CMS explains public aggregate claims cannot reconstruct that journey. | Community comparisons retain public surveillance and study references; the new voice-to-action section explains what county context can and cannot show. | No claim of a measured local pre-diagnosis cost. Controlled claims access, methods and study design remain future work. |
| Oct 8, 49:12–51:58: discussion emphasizes inspectable information, human review and avoiding diagnostic interpretation. | Personal records remain reviewable; the new planning section asks patients, caregivers and community partners to review priorities and decisions. | No clinical interpretation or regulatory certification is inferred from this meeting. |
| Oct 15, 14:11–24:49: advocates describe burdens beyond bills, unpaid care, isolation and barriers to practical support. | Visible community action options now include caregiving/daily life, food/housing/benefits, work/school/relationships and getting to care. | No personal story, clinical claim or speaker's numerical assertion is imported into a population model. |
| Oct 15, 33:49–40:37: severe illness can prevent self-report, and memory and functioning vary. | The community summary explanation calls out accessible participation and authorized caregiver options; existing personal caregiver/daily-life fields remain separate. | No validated proxy scale, longitudinal tracking or new caregiver collection is claimed. |
| Oct 15, 11:35–14:11 and 44:42–47:42: sample size, variability, denominators and transfer between populations matter. | The fictional comparable-cohort example is now reachable in Community. It preserves missing answers, residence, phase, period and small-group withholding. | Five examples are a demonstration threshold, not proof of precision or privacy. Real volunteer aggregates cannot establish county prevalence. |
| Oct 15, 54:29–57:30: use relevant evidence with transparent assumptions; illustrative person scenarios can help when data are incomplete. | Editable round trips × assumed price demonstrates one invented person's travel spending over 30 days, with explicit arithmetic. | No fabricated price quote, savings, county demand estimate or addition to published societal costs. |
| Policy usefulness across both meetings | A visible need → county context → possible action → participants → measures pathway and downloadable brief; also included in the existing county brief. | Partner agreement, actual implementation and outcome evaluation are still needed. |

## Where to find the changes

- Start page: patient voices and community needs message.
- Community Burden & Action: after the two-county cost illustration, before the personal-record invitation, find **Patient voices → community action**.
- Choose a support priority to update the proposed action and measures.
- Open **See how comparable patient reports could be summarized** for the six invented cards.
- Open **Explore an assumed travel-cost scenario** for adjustable assumptions.
- Download **patient voice-to-action brief**, or use the existing community planning brief, which includes the selected pathway.

## Real contribution requirements still outstanding

Consent and accessible participation; appropriate caregiver permission and attribution; private durable storage; duplicate handling; common fields and periods; disclosure and statistical review; retention/deletion; partner responsibilities and evaluation. Shared real collection remains off by default. These changes do not automatically aggregate private session records or enable public collection.

The participant-provided county prevalence paper mentioned around Oct 15 43:59 was not included in the PDFs. Its link is now supplied in the October 15 chat (01:05:31), but the document and formulas have not been evaluated or adopted. Neither the minimum-N discussion nor an advocate's clinical statements are treated as universal rules or verified medical evidence.

## Additional research leads from September 24

American Time Use Survey for unpaid-care definitions/context (25:03); MEPS for comparable spending measurement across payers, subject to sparse samples; HCUP for hospital-use research (59:11); and informal-care economic methods discussed around 56:42 and 1:00:42. Links posted in meeting chat are not included in this transcript. These leads have not been downloaded, priced, licensed, validated or incorporated as new numeric inputs. No All of Us exports or participant-shared synthetic records were accessed; their permissions cannot be established by the transcript.

## October 8 and October 15 meeting chats

Read `Chat Office Hours 10_8.txt` and `Chat - Office Hours 10_15.txt` in addition to the four PDFs. The chat clock differs from the transcript clock; citations below use chat timestamps. Comments directed to other teams can inform design but are not endorsements of PathwayAI.

| Chat evidence | Implication for PathwayAI | Status |
| --- | --- | --- |
| Oct 15, 00:43:42: John Phillips identifies organizing relevant evidence for accessing/maintaining benefits as a useful application target. | Prioritize reviewed support summaries and benefits-conversation preparation, not just charts. | Existing benefits checklist; newer review package also retains food/housing and benefits support summaries. No application submission, eligibility decision or guaranteed faster approval. |
| Oct 15, 00:53:50–00:54:17: NHIS for health context, MEPS for expenditures, ATUS for relevant time-use estimates, ACS for local context; caregiving earnings require combined data and assumptions. | Choose sources by the question; do not equate health prevalence, spending, time and county context. | Recorded as research directions. No new numerical inputs imported. |
| Oct 15, 00:57:37: John Phillips suggests stylized examples for lost opportunities, caregiving, labor, relationships and education. | Strengthens the rationale for the visible nonmedical-burden themes and transparent invented-person scenario. | Travel scenario implemented; earnings and cumulative opportunity valuation remain future methods work. |
| Oct 15, 00:59:32: Thomas Selden clarifies that MEPS/NHIS can use family respondents, not exclusively the affected person's self-report. | Preserve who supplied information. Do not assume severe patients are universally absent from those surveys or that proxy observations equal patient self-report. | Existing personal reporter roles and separate caregiver fields retained. No new survey representation claim. |
| Oct 15, 01:03:35: be transparent about sample size. | Count usable answers and missing values and state the population represented. | Fictional cohort shows six invented cards and five usable answers; not county prevalence or a privacy/precision guarantee. |
| Oct 8, 00:35:21: consider relevant services local to the patient. | Connect planning to usable referral and support pathways; location counts alone are insufficient. | Planning actions include service feasibility and follow-up; actual availability requires confirmation. |

### Links now available for follow-up (not validated source inputs)

- ResDAC: https://www.resdac.org/ (Oct 8, 00:39:22).
- RECOVER data: https://recovercovid.org/data (Oct 8, 00:24:07); Long COVID research, not automatically transferable to Lyme.
- National Academies project: https://www.nationalacademies.org/projects/HMD-HCS-22-07 (Oct 8, 00:21:58); disability-related research lead, not individual eligibility advice.
- USDA SNAP statistics/research: https://www.ers.usda.gov/topics/food-nutrition-assistance/supplemental-nutrition-assistance-program-snap/key-statistics-and-research (Oct 8, 00:58:49); population context does not establish local demand.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11753895/ and https://pubmed.ncbi.nlm.nih.gov/40371440/ (Oct 15, 00:30:02–00:31:10). The sender explicitly said these were quick-search examples they had not read. Do not describe them as reviewed recommendations.
- The October 15 chat also links participant-authored SNAP, suicide-estimate and county-prevalence documents. They are not official benefit procedures, verified clinical findings or validated prevalence models. Their full contents have not been reviewed or adopted.

Questionnaire names in the chat are research leads, not proof of licensing, suitability, validation in this population or diagnostic utility. No questionnaire or clinical scoring has been added on that basis. Clinical and benefits-law statements in discussion require authoritative verification before publication as guidance. Meeting-notetaker commands and autogenerated action items are not instructions to this implementation; no participants have been contacted.
