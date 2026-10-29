# Community workflow review — initial findings

Review date: 2026-10-28. Branch: `review/community-dutchess-lani`.
Scope: inspect and report first; preserve application behavior. No deployment or merge.
Comparison source: the user-supplied public TOPx submission, “Lani - Hidden Symptoms Visible,” attributed to Scott Savitt, describing Lani Companion Health version 1.2.4. Linked overview: https://www.lani.health/ ; iPhone listing: https://apps.apple.com/us/app/lani-companion/id6767335499 ; Android listing: https://play.google.com/store/apps/details?id=app.lani.health . The supplied text was reviewed on 2026-10-28; the website, store listings and mobile product were not independently inspected. Its relative “1 week ago” label does not establish an exact publication date. Clinical screening and voice-companion features are excluded from the proposed work.

## Comparison with Lani's publicly described capabilities

| Capability described in supplied Lani submission | Existing PathwayAI behavior | Implication for PathwayAI |
| --- | --- | --- |
| Gentle voice/text check-ins; dated Health Intelligence Story; selective sharing with caregivers or care teams | Optional text story organization, editable visit summaries, downloadable records and session-only dated observations | Preserve working preparation tools. Do not build a competing voice companion or imply PathwayAI already provides durable longitudinal records. |
| Resource navigation for food, housing, transportation and medication costs with HRSA/CDC/Census/USDA context | Existing care access, bills, transport and benefits guidance; county resource/context panels | Resource links alone are not a defensible distinction. Center a county decision question, evidence limits, feasibility, responsibilities and follow-up instead. |
| Structured social/emotional screening, including named instruments | PathwayAI's burden and support-needs recording is not such screening | Do not copy screens, scoring, clinical triage or diagnosis features. Describe daily-life records as reported experience. |
| CMS/Medicare, VA and Humana authorized-record sandbox integrations | Public Medicare county context; no equivalent authorized-personal-record integration established by this inspection | Clearly distinguish public area statistics from personal payer/health-record access. No integration parity claim. Sandbox success is not evidence of production integration. |
| Multilingual companion and cross-condition reuse | Limited notes-language aids and opt-in English translation; interface is not fully translated | State current language coverage accurately. Improve assisted/offline county review and plain language without promising a universal multilingual companion. |
| Faster diagnosis, lower spending and better outcomes stated as goals | No demonstrated clinical benefit, savings, adoption or county partnership | Keep both products' goals separate from evaluated outcomes. Evaluate PathwayAI initially on task completion, interpretation, brief usefulness and verified follow-up, not clinical-effect claims. |

**Distinct deliverable:** an inspectable county discussion brief linking observed public data, study-based cost assumptions, unmeasured burden, a proposed support response and a review plan. Lani's supplied description centers the person's journey; it does not describe this county decision artifact. That is a distinction in the supplied descriptions, not a claim that Lani lacks any unmentioned capability.

## Position and existing capabilities

Proposed positioning: **PathwayAI helps county teams interpret public Lyme burden evidence, choose a support-planning question, and bring a sourced brief to residents and service partners.** Personal preparation supports this purpose without requiring patients to contribute data.

Already implemented:

- `app.py:policy89`: national evidence, Dutchess/Orange comparisons, planning, and methods tabs. No patient intake is required for county planning. Personal support remains accessible separately.
- `county_burden_report.py`: Dutchess/Orange report builder, public-evidence preview, PDF download through `report_download.py`, and CSV methods export. Proposed actions, capacity/funding checks, evaluation and scope limitations already exist.
- `community_action.py`: five support priorities with proposed partners and measures. A separate action brief includes a clearly labeled fictional six-card example, not live reports.
- `burden_framework.py`, `county_cost_scenario.py`, and verification JSON files: existing cost perspectives, source records and explicit transfer assumptions. Personal money paid, workdays and caregiver hours are already separated; modeled work loss is not added to cash spending.
- Notes and reviewed edits are reused across care/bite navigation; story-derived defaults, compact PDFs, reading modes and optional daily-life records already reduce repeated entry.
- External story AI is optional; translation requires consent and a click. County report generation uses public local files and no personal session fields.

## Priority gaps and proposed changes

| Priority | Gap found in current implementation | Recommended bounded improvement |
| --- | --- | --- |
| P0 | Community opens with the U.S. burden tab; the county report is inside the third tab. The existing walkthrough starts with personal intake and clinical testing. | Add a short county-first path: Dutchess evidence → one planning question → brief. Keep all existing tabs and patient workflows. |
| P0 | Report highlights a single transferred societal mean: 1,060 × $2,032 = $2,153,920 in 2016 dollars. It gives limitations but no structured uncertainty summary. | Label it an illustration at every headline; distinguish sampling, transfer, surveillance and coverage uncertainty. Do not invent confidence bounds. Mean/median alternatives are scenarios, not a confidence interval. |
| P0 | Existing verification files carry check dates, page numbers and hashes; the county report exports only part of this metadata. Hook verification explicitly excludes separately retrieved tables. | Export source ID, publication/data/dollar years, page/table/section, verification status/date and supplied-file hash per claim. Recheck original tables before upgrading verification claims. |
| P0 | County PDF describes the combined societal perspective but lacks a compact medical/household/daily-life matrix. | Show medical resource costs, household payments/financial hardship, work/caregiver time and unmonetized daily-life impacts in separate rows. Explain payer overlap; never sum medical costs, patient bills and societal totals. Missing local measurements remain unknown. |
| P0 | Shared collection can be enabled with a flag and writes local CSVs. Consent timestamps and reduced fields exist; withdrawal, retention enforcement, unique-contributor controls and release review are not established. | Keep collection disabled. Require a reviewed data lifecycle and governed storage before collecting real records. Do not present small-group thresholds as sufficient privacy protection. |
| P1 | Repeated county/topic selectors occur across report and planning templates. The report does not provide named local owners, current capacity, budget or a review date. | Reuse the selected county/topic and offer an optional local-review worksheet. Mark contacts, capacity, budget and responsibilities as unverified until reviewed; do not imply commitments. |
| P1 | Privacy notice accurately says server session; another note calls notes “saved for this browser session.” | Use consistent server-session wording, clarify loss on disconnect/restart, and preserve explicit limits of the clear-session action. |

## Privacy and persistence audit

Code inspection, not a hosting/security certification:

| Surface | Current behavior | Remaining assurance gap |
| --- | --- | --- |
| Personal notes/records | Server-side Streamlit session state; explicit clear-session action (`app.py:clear_session_and_return`). | Hosting logs/backups/session expiration and deletion need operational verification. Clearing does not erase downloads or provider copies. |
| Story organization/translation | Opt-in OpenAI request; `store=false`; local story fallback; language/reporter included for translation. | Provider/account retention still applies. Confirm the actual request payload and consent invalidation when notes change with focused tests before making stronger claims. |
| AI rate limiting | Local `.pathwayai_ai_limits.sqlite3`: keyed connection identifier and request timestamps; expired rows removed during checks. | Persistent metadata remains separate from patient narratives. Retention depends on future checks; idle databases/backups need a policy. Local story organization also performs a quota check, so “AI off” must not be advertised as zero disk writes. |
| Shared Patient Voice | Disabled by default. Enabled path stores county, period, phase, cost bands, workdays, caregiver hours, barrier and consent time in local CSV. No raw story/ZIP/exact spending in v88 schema. | Sensitive combinations and timestamps remain; duplicate prevention is session-level, not verified unique people. No evidenced participant deletion/withdrawal workflow, consent-policy version or storage governance. Legacy CSV writer/reader also exists and needs coverage. |
| Public summaries | Comparable phase/period groups and at least five usable responses per measure; explicit voluntary/nonrepresentative caveat. | Differencing/repeated releases, linkage and rare combinations require disclosure review. |
| County downloads | Deterministic public evidence and proposed planning actions. PDF conversion is handled by the shared download wrapper. | Keep personal-state exclusion regression checks. Generated/downloaded files have their own persistence. |
| Survey/email handoffs | Separate survey and pilot-enquiry links; app warns these are separate from personal records. | Review destination forms, consent, ownership, access, retention and downstream sharing; no verified end-to-end deletion guarantee. |

## Five-minute Dutchess demonstration

Use a fresh fictional-data-only session, external AI off and shared collection disabled. No patient story is needed.

1. **0:00–0:35:** Open Community Burden & Action directly. State the county planning purpose and that no county adoption or live resident aggregate is claimed.
2. **0:35–1:25:** County comparison → Dutchess: 1,060 reported cases and 355.5 per 100,000 in 2024. Explain residence versus exposure and reported cases versus all infections. Show the source rather than claiming these figures measure service demand.
3. **1:25–2:25:** Plan community support → Dutchess report. Explain the $2,153,920 illustration in 2016 dollars, transfer assumption and excluded populations/longer-term impacts. Keep optional inflation off: the available 2025 workbook omits October and is not a verified annual-average restatement.
4. **2:25–3:35:** Select “Care without insurance and medical bills.” Review the planning question, possible partners, appointment/staffing/funding checks and unresolved local demand. Avoid promises of access, benefit or savings.
5. **3:35–4:25:** Download the county PDF and methods CSV. Show source status, gaps and proposed follow-up. Keep the separate synthetic action-template brief out of the primary evidence presentation.
6. **4:25–5:00:** Ask the county team to identify a reviewer, validate local services and decide whether to explore a small support pilot. Explain that resident contribution would require separate governance and consent.

## Validation and next step

The current Dutchess report was generated using the existing builder/PDF renderer with no personal inputs; its 1,060 × $2,032 arithmetic and transfer disclaimer were checked. Preview artifacts are outside the checkout at `/workspace/pathwayai-review/`. These demonstrate current output, not newly improved report content or freshly verified source tables.

Prior onboarding suite baseline: 96 executed, 93 passed, 3 UI/test errors. This review has not changed application code or rerun the entire suite. The missing care navigation button/headings and stale expectations should be resolved in a separate scoped implementation while preserving working flows.

The Lani comparison above is limited to the supplied public submission, not an independent hands-on product evaluation. Next implement the P0 presentation and brief improvements with focused report-provenance, privacy-exclusion and navigation checks. No screening or voice feature work is proposed.
