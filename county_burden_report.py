"""Public-evidence county planning briefs.

No patient records, session stories, external AI, or shared-data writes.
"""

from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
import json

from community_action import ACTION_OPTIONS
from inflation_context import inflation_metadata

BASE = Path(__file__).resolve().parent
REPORT_VERSION = "1.1"
LOCAL_FIELDS = {
    "partners": "Local partners to approach",
    "resources": "Existing resources and date checked",
    "capacity_gaps": "Known capacity gaps",
    "notes": "Local planning notes",
}


def load_county_registry():
    data = json.loads((BASE / "data/county_report_registry.json").read_text())
    if data["schema_version"] != 1:
        raise ValueError("Unsupported county registry version")
    result = {}
    fips_seen = set()
    for row in data["counties"]:
        if row["name"] in result or row["fips"] in fips_seen:
            raise ValueError("Duplicate county name or FIPS")
        if len(row["fips"]) != 5 or not row["fips"].isdigit():
            raise ValueError("County FIPS must contain five digits")
        for field in ("cases_record", "rates_record"):
            if Path(row[field]).name != row[field]:
                raise ValueError("Source records must be local data filenames")
        result[row["name"]] = row
        fips_seen.add(row["fips"])
    return result


COUNTY_REGISTRY = load_county_registry()
COUNTIES = {name: row["fips"] for name, row in COUNTY_REGISTRY.items()}


def _load(filename):
    return json.loads((BASE / "data" / filename).read_text(encoding="utf-8"))


def _source(record, source_id, purpose, period, filename):
    """Carry existing verification metadata without upgrading its status."""
    return {
        "source_id": source_id,
        "purpose": purpose,
        "title": record.get("source", record.get("document_title", "See original source")),
        "period": period,
        "url": record["source_url"],
        "checked_on": record.get("source_checked_on", record.get("verified_on", "Not recorded")),
        "page": record.get("pdf_page"),
        "verification": record.get(
            "verification",
            record.get("verification_scope", record.get("scope", "See verification record.")),
        ),
        "supplied_file_sha256": (
            record.get("uploaded_pdf_sha256")
            or record.get("uploaded_text_sha256")
            or "Not recorded"
        ),
        "verification_record": "data/" + filename,
    }


def build_report(county, priority, restate=False, local_context=None):
    if county not in COUNTIES or priority not in ACTION_OPTIONS:
        raise ValueError("Choose a supported county and planning priority.")

    config = COUNTY_REGISTRY[county]
    cases_file = config["cases_record"]
    rates_file = config["rates_record"]
    hook_file = "hook_2022_article_verification.json"
    cases = _load(cases_file)
    rates = _load(rates_file)
    hook = _load(hook_file)
    count = cases["verified_lyme_case_counts"][config["county_key"]]
    unit = hook["societal_mean"]
    import math
    rate = rates["verified_rates"][config["county_key"]]
    state_rate = rates["verified_rates"][config["state_rate_key"]]
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("A reviewed nonnegative integer case count is required")
    for value in (rate, state_rate):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("Reviewed finite nonnegative county and state rates are required")
    total = count * unit

    report = {
        "report_version": REPORT_VERSION,
        "generated_on": date.today().isoformat(),
        "local_context": {
            key: str((local_context or {}).get(key, "")).strip()[:800]
            for key in LOCAL_FIELDS
        },
        "county": county,
        "state": config["state"],
        "county_fips": COUNTIES[county],
        "reported_cases": count,
        "case_year": config["year"],
        "reported_rate_per_100000": rates["verified_rates"][config["county_key"]],
        "state_reported_rate_per_100000": rates["verified_rates"][config["state_rate_key"]],
        "study_societal_mean_usd": unit,
        "study_dollar_year": 2016,
        "illustrative_total_2016_usd": total,
        "study_population": (
            "613 participants in the societal analysis; reported cases "
            "recruited in four high-incidence states during 2014–2016."
        ),
        "cost_perspective": (
            "Societal: medical, nonmedical and productivity costs. "
            "These components are already included."
        ),
        "formula": (
            f"{count:,} reported cases × USD {unit:,} study mean "
            f"= USD {total:,} (2016 dollars)."
        ),
        "transfer_assumption": (
            "Applying this study mean to reported county cases is an "
            "assumption; the result is not measured local spending."
        ),
        "other_assumptions": (
            "No adjustment for underreporting or local case mix. "
            "No causal savings or disability probabilities are inferred."
        ),
        "cost_domains": [
            {
                "domain": "Medical resource costs",
                "measure": "Published societal medical-cost component",
                "local_status": "Not measured locally by this report",
                "interpretation": (
                    "Medical resource costs are not the same as a "
                    "household's medical bills or money paid."
                ),
            },
            {
                "domain": "Household financial impacts",
                "measure": (
                    "Money paid for care, travel and other expenses; "
                    "unpaid bills and financial hardship"
                ),
                "local_status": "Not measured locally by this report",
                "interpretation": (
                    "Keep spending, outstanding balances and hardship "
                    "separate. Do not add patient bills to societal totals."
                ),
            },
            {
                "domain": "Work and unpaid caregiving",
                "measure": "Missed workdays and unpaid caregiver hours",
                "local_status": "Not measured locally by this report",
                "interpretation": (
                    "Report time in its original units. Any monetary "
                    "valuation requires explicit assumptions and checks "
                    "for overlap with published productivity costs."
                ),
            },
            {
                "domain": "Daily-life and participation impacts",
                "measure": (
                    "Limits in daily activities, school, rest, "
                    "relationships and participation"
                ),
                "local_status": "Not measured locally by this report",
                "interpretation": (
                    "Do not assign a dollar value or infer Lyme-attributable "
                    "county disability from general population measures."
                ),
            },
        ],
        "uncertainty": [
            {
                "type": "Surveillance",
                "meaning": (
                    "Reported cases are not all infections. County of "
                    "residence does not establish exposure location."
                ),
            },
            {
                "type": "Study sampling and measurement",
                "meaning": (
                    "The source study has recruitment, recall and "
                    "cost-attribution limitations."
                ),
            },
            {
                "type": "Transfer to this county",
                "meaning": (
                    "Local case mix, access, prices and illness duration "
                    "may differ from the study population."
                ),
            },
            {
                "type": "Coverage of burden",
                "meaning": (
                    "Excluded populations and longer-term effects are not "
                    "fully represented. Missing burden is not zero."
                ),
            },
            {
                "type": "Statistical precision",
                "meaning": (
                    "No county confidence interval is calculated. "
                    "Mean/median alternatives would be scenarios, "
                    "not confidence bounds."
                ),
            },
        ],
        "priority": priority,
        "planning": dict(ACTION_OPTIONS[priority]),
        "evidence_gaps": [
            "Lyme-attributable county disability and duration",
            "Continuing costs beyond the study follow-up",
            "Local unmet care and support needs",
            "Experiences of excluded or underrepresented populations",
        ],
        "feasibility_checks": [
            "Review local needs with residents and caregivers.",
            "Offer assisted and offline participation.",
            "Verify services, eligibility and appointment capacity.",
            "Confirm interpreter access and accessibility.",
            "Identify responsible partners, staff time, costs and funding.",
            "Agree consent, access, retention and deletion before collection.",
        ],
        "review_worksheet": [
            "County reviewer or team: ____________________",
            "Review date: ____________________",
            "Resident/caregiver review arrangements: ____________________",
            "Verified services and date checked: ____________________",
            "Capacity or eligibility gaps: ____________________",
            "Responsible partner, if agreed: ____________________",
            "Staff time and estimated program cost: ____________________",
            "Potential funding source, if identified: ____________________",
            "Next decision and follow-up date: ____________________",
        ],
        "evaluation": (
            "Agree a common reporting period and baseline. Record missing "
            "answers, support received and unresolved needs. Before/after "
            "changes alone do not establish causality or savings."
        ),
        "sources": [
            _source(cases, "NYSDOH_CASES_2024",
                    "Reported cases by county of residence", "2024", cases_file),
            _source(rates, "NYSDOH_RATES_2024",
                    "Reported rates per 100,000 residents", "2024", rates_file),
            _source(hook, "HOOK_2022_SOCIETAL", "Societal study mean",
                    "2016 dollars; recruitment 2014–2016", hook_file),
        ],
        "privacy": (
            "Public evidence and proposed planning actions only. "
            "No session stories, personal records or synthetic patient "
            "cards are included."
        ),
        "scope": (
            "Discussion brief, not a county demand assessment, benefits "
            "decision, funded service or adopted county plan."
        ),
        "inflation": None,
    }
    if restate:
        meta = inflation_metadata()
        factor = Decimal(str(meta["factor"]))
        report["inflation"] = {
            **meta,
            "restated_unit_usd": float(Decimal(str(unit)) * factor),
            "restated_total_usd": float(Decimal(str(total)) * factor),
        }
    return report


def report_text(report):
    from report_download import TAGLINE

    r = report
    lines = [
        f"PathwayAI | {r['county']} County Lyme Burden & Action Brief",
        TAGLINE,
        f"Version {r['report_version']} · Generated {r['generated_on']}",
        "", "PURPOSE",
        "Help county teams interpret evidence and review one support decision.",
        "No patient intake is required to use this brief.",
        r["scope"],
        "", "1. OBSERVED PUBLIC EVIDENCE",
        (f"Reported Lyme cases: {r['reported_cases']:,} in "
         f"{r['case_year']} · FIPS {r['county_fips']}."),
        (f"Reported rate: {r['reported_rate_per_100000']:g} per 100,000. "
         f"New York State: {r['state_reported_rate_per_100000']:g}."),
        "Source IDs: NYSDOH_CASES_2024; NYSDOH_RATES_2024.",
        ("Reported cases describe residence, not all infections, "
         "exposure location or unmet service demand."),
        "", "2. STUDY-BASED ECONOMIC ILLUSTRATION",
        "Not observed county spending, a current budget or predicted savings.",
        r["formula"],
        "Source ID: HOOK_2022_SOCIETAL.",
        r["study_population"], r["cost_perspective"],
        r["transfer_assumption"], r["other_assumptions"],
        ("The study excluded non-English speakers and nonacute disease; "
         "it does not represent every local household."),
        "", "3. KEEP DIFFERENT IMPACTS SEPARATE",
    ]
    for domain in r["cost_domains"]:
        lines.extend([
            domain["domain"], "Measure: " + domain["measure"],
            "Local evidence: " + domain["local_status"],
            domain["interpretation"], "",
        ])
    lines.append("4. UNCERTAINTY AND LIMITS")
    for item in r["uncertainty"]:
        lines.append(item["type"] + ": " + item["meaning"])
    if r["inflation"]:
        m = r["inflation"]
        lines.extend([
            "", "OPTIONAL PURCHASING-POWER COMPARISON",
            (f"Per case: USD {m['restated_unit_usd']:,.0f}; "
             f"county illustration: USD {m['restated_total_usd']:,.0f}."),
            ("General inflation only; original 2016-dollar values remain "
             "the primary illustration."),
            ("2025 has 11 observed months; October is missing. "
             "No imputation. This is not a verified official "
             "annual-average restatement."),
            (f"Base index: {m['base_index']}; "
             f"target index: {m['target_index']}; factor: {m['factor']}."),
            m["source_url"],
            "Source workbook SHA-256: " + m["source_sha256"],
        ])
    plan = r["planning"]
    lines.extend([
        "", "5. SUPPORT DECISION TO EXPLORE", r["priority"],
        "Planning question: " + plan["decision"],
        "Possible response: " + plan["action"],
        "Potential partners to approach: " + plan["participants"],
        ("These are proposed discussion topics, not findings about "
         "local demand or commitments from partners."),
        "", "6. CHECK FEASIBILITY",
    ])
    lines.extend("- " + item for item in r["feasibility_checks"])
    lines.extend(["", "7. ADDITIONAL BURDEN TO MEASURE"])
    lines.extend("- " + item for item in r["evidence_gaps"])
    lines.extend([
        "", "8. COUNTY REVIEW WORKSHEET",
        "Complete locally; blank fields are not verified arrangements.",
    ])
    lines.extend(r["review_worksheet"])
    lines.extend(["", "LOCALLY COMPLETED PLANNING — UNVERIFIED",
                  "Optional staff-entered context; not public-source findings or partner commitments."])
    for key, label in LOCAL_FIELDS.items():
        lines.append(label + ": " + (r["local_context"][key] or "Not completed"))
    lines.extend([
        "", "9. FOLLOW-UP", "Candidate measures: " + plan["measure"],
        r["evaluation"], "", "SOURCES AND VERIFICATION",
        ("Verification metadata describes prior source checks. "
         "Generating this report does not reverify the original sources."),
    ])
    for source in r["sources"]:
        lines.extend([
            "", source["source_id"] + " — " + source["purpose"],
            source["title"], "Period: " + source["period"], source["url"],
            "Check date: " + str(source["checked_on"]),
            "PDF page: " + str(source["page"] or "See verification record"),
            "Status: " + source["verification"],
            "Supplied-file SHA-256: " + source["supplied_file_sha256"],
            "Repository record: " + source["verification_record"],
        ])
    lines.extend(["", r["privacy"], r["scope"]])
    return "\n".join(lines)


def report_csv_rows(report):
    row = deepcopy(report)
    for key, value in list(row.items()):
        if isinstance(value, (dict, list)):
            row[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return [row]


def show_county_report():
    import streamlit as st
    from burden_framework import csv_bytes
    from report_download import branded_download_button

    st.markdown("### Download a county burden & action report")
    st.write(
        "For county teams: review public evidence, explore one support "
        "decision, and download a brief for local discussion. "
        "No patient story or contribution is required."
    )
    left, right = st.columns(2)
    with left:
        county = st.selectbox("County for the report", list(COUNTIES),
                              key="county_report_county")
    with right:
        priority = st.selectbox("Support priority to explore", list(ACTION_OPTIONS),
                                key="county_report_priority")
    restate = st.checkbox(
        "Include the optional 2025 purchasing-power comparison",
        value=False, key="county_report_inflation",
    )
    if restate:
        st.caption(
            "Uses 11 available months; October is missing. "
            "This is not a verified annual-average restatement."
        )
    with st.expander("Add optional local planning context"):
        st.caption("For public planning information only. Do not enter patient details or confidential information. These notes are held in the server session and included in your downloads, not saved as a shared county record.")
        local_context = {
            key: st.text_area(label, max_chars=800,
                              key=f"county_local_{county}_{key}")
            for key, label in LOCAL_FIELDS.items()
        }
    report = build_report(county, priority, restate, local_context)
    with st.container(border=True):
        st.markdown(f"**{county} County · Public evidence**")
        st.write(
            f"{report['reported_cases']:,} reported cases in {report['case_year']} · "
            f"{report['reported_rate_per_100000']:g} per 100,000."
        )
        st.markdown("**Study-based illustration · 2016 dollars**")
        st.write(f"USD {report['illustrative_total_2016_usd']:,.0f}")
        st.caption("Not measured local spending, a county budget, or predicted savings.")
        st.write(report["transfer_assumption"])
        st.markdown("**Decision to explore**")
        st.write(report["planning"]["decision"])
    branded_download_button(
        "Download county burden & action report (PDF)",
        report_text(report).encode("utf-8"),
        file_name=f"PathwayAI_{county}_County_Burden_Action_Report.txt",
        mime="text/plain", key="county_report_pdf", type="primary",
    )
    from county_executive_pdf import executive_pdf
    st.download_button(
        "Download one-page executive brief (PDF)", executive_pdf(report),
        file_name=f"PathwayAI_{county}_Executive_Brief.pdf",
        mime="application/pdf", key="county_executive_pdf",
    )
    st.download_button(
        "Download full report as text", report_text(report),
        file_name=f"PathwayAI_{county}_County_Burden_Action_Report.txt",
        mime="text/plain", key="county_report_text",
    )
    with st.expander("Separate medical, financial and daily-life impacts"):
        st.dataframe(report["cost_domains"], hide_index=True, use_container_width=True)
        st.write(
            "These categories overlap in published economic studies. "
            "Do not sum them into a new total."
        )
    with st.expander("Review uncertainty"):
        for item in report["uncertainty"]:
            st.markdown(f"**{item['type']}:** {item['meaning']}")
    with st.expander("Inspect calculations, sources and report data"):
        st.text(report["formula"])
        st.write(report["transfer_assumption"])
        for source in report["sources"]:
            st.markdown(
                f"[{source['source_id']}: {source['purpose']}]({source['url']})"
            )
            st.caption(
                f"Period: {source['period']} · Checked: {source['checked_on']} · "
                f"{source['verification']}"
            )
        st.download_button(
            "Download report data and methods (CSV)",
            csv_bytes(report_csv_rows(report)),
            file_name=f"PathwayAI_{county}_County_Burden_Action_Report.csv",
            mime="text/csv", key="county_report_csv",
        )
    with st.expander("Need a draft for another county?"):
        st.write("Current verified coverage: " + ", ".join(COUNTIES) + ". Additional counties need reviewed public counts, rates and source records before a numerical brief can be generated.")
        st.download_button(
            "Download county data request checklist",
            "COUNTY DRAFT PREPARATION — no request is sent automatically.\n"
            "County/state and five-digit FIPS:\nReporting year:\n"
            "Official case count and definition:\nOfficial county/state rates and units:\n"
            "Source URLs, table/page, retrieval/check dates and verification status:\n"
            "Missing/suppressed values (never substitute zero):\n"
            "Local partners/resources/capacity to review:\n"
            "No patient information required. Review original sources before registering a county.\n",
            file_name="PathwayAI_County_Data_Checklist.txt", mime="text/plain",
            key="county_data_checklist",
        )
    st.caption(
        "Before proposing a pilot: review needs with residents, verify "
        "services and capacity, and agree responsibilities, costs, "
        "funding and follow-up. Shared patient collection remains "
        "a separate consent and governance decision."
    )
