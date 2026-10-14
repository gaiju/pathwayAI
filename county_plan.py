"""Verified summaries of the user-provided public county CHIP, not Lyme estimates."""

CHIP_URL = "https://www.dutchessny.gov/Departments/DBCH/Docs/Dutchess-County-Community-Health-Improvement-Plan.pdf"
CHA_URL = "https://www.dutchessny.gov/Departments/DBCH/Docs/DCCHA2025.pdf"


def combined_planning_rows():
    return [
        {"Lyme evidence already shown": "Tick exposure context and prevention guidance; no measured PathwayAI prevention effect",
         "County plan context": "General disparities in access across geographic areas (printed p. 5)",
         "Response to evaluate": "Discuss accessible tick-prevention education and routes to appropriate clinical care",
         "What to measure": "Reach of prevention information; reported barriers; time to appropriate care"},
        {"Lyme evidence already shown": "NYSDOH 2024: Dutchess 355.5 reported cases per 100,000; Orange 237.0",
         "County plan context": "Gaps in care across geographic areas and disability groups (printed p. 5)",
         "Response to evaluate": "Ask local partners where Lyme referral and follow-up access needs attention",
         "What to measure": "Time to a visit; completed referrals; reported unmet needs"},
        {"Lyme evidence already shown": "Published medical and societal cost references; different study populations and dollar years",
         "County plan context": "Insurance coverage and care access were leading resident-voted topics (printed p. 7)",
         "Response to evaluate": "Review financial barriers among consenting Lyme participants; consider coverage navigation",
         "What to measure": "Patient-paid costs over one period; assistance connections completed"},
        {"Lyme evidence already shown": "Work and caregiver time are burden categories; local shared measurements are not yet available",
         "County plan context": "Disability-related care disparities (printed p. 5)",
         "Response to evaluate": "Review work, caregiver and access support needs with participants",
         "What to measure": "Missed workdays; caregiver hours; support still needed"},
    ]


def show_combined_planning_evidence():
    import streamlit as st

    st.markdown("#### Connect Lyme evidence with local priorities")
    st.write("Connect Lyme findings with the county health plan. Use the suggested actions and measures in partner discussions.")
    st.table(combined_planning_rows())

PLAN_CONTEXT = {
    "source": "Dutchess County Community Health Improvement Plan 2025–2030",
    "source_url": CHIP_URL,
    "geography": "Dutchess County, New York",
    "plan_period": "2025–2030",
    "source_checked_on": "2026-10-14",
    "verification": "Read from the user-provided full public plan PDF",
    "evidence_type": "County policy and general community health context; not Lyme cost data",
    "priorities": [
        "Nutrition Security",
        "Preventive Services for Chronic Disease Control and Prevention",
        "Primary Prevention, Substance Misuse, and Overdose Prevention",
    ],
    "findings": [
        {"finding": "The plan describes health disparities between the urban/suburban west and rural east, and by race/ethnicity and disability status.",
         "printed_page": 5, "pdf_page": 6},
        {"finding": "In informal priority voting at six community events, 830 residents participated. Health Insurance Coverage and Access to Care followed Mental Wellbeing and Substance Use as a leading topic.",
         "printed_page": 7, "pdf_page": 8,
         "limitation": "Informal priority voting with two stones per participant; not prevalence, a random sample or Lyme patient evidence."},
        {"finding": "The plan describes blood-pressure screening through the Mobile Health Unit and Medical Reserve Corps, with referrals to primary care or Sun River Health.",
         "printed_page": 10, "pdf_page": 11,
         "limitation": "A hypertension intervention, not a commitment to Lyme screening or treatment."},
        {"finding": "The plan describes social-care referrals through Hudson Valley Care Coalition and Unite Us, with follow-up and outcome tracking.",
         "printed_page": 9, "pdf_page": 10,
         "limitation": "PathwayAI has no integration or partnership with these services."},
    ],
}


def show_county_plan_context(note):
    import streamlit as st

    st.markdown("#### Local priorities: access and coverage")
    st.write("Dutchess County’s 2025–2030 health plan describes geographic and disability-related gaps in care. "
             "Insurance coverage and care access were leading topics in resident priority voting.")
    st.markdown(f"[Read the Dutchess health plan]({CHIP_URL}) · [Community health assessment]({CHA_URL})")
    note("The county plan describes general health needs, not Lyme-specific costs or an adopted Lyme program.")
    with st.expander("Connect county priorities with the burden people report"):
        st.table([
            {"County plan finding": "Geographic and disability-related gaps in care",
             "Possible use of PathwayAI records": "With consent, compare reported care barriers, travel spending and time lost among contributors. Keep residence separate from exposure."},
            {"County plan finding": "Insurance coverage and care access matter to residents",
             "Possible use of PathwayAI records": "Reuse reviewed cost records to identify financial pressure. Compare the same cost categories and reporting periods."},
            {"County plan finding": "Existing screening and referral pathways",
             "Possible use of PathwayAI records": "Discuss appropriate referral and follow-up with partners. Measure connections completed and support still needed."},
        ])
        st.write("These are PathwayAI planning ideas. They are not county commitments, "
                 "measured effects or an adopted Lyme program.")
    note("County source: Dutchess CHIP 2025–2030, printed pp. 5, 7, 9–11 (PDF pp. 6, 8, 10–12). "
         "Resident voting involved 830 participants at six events; this is not a Lyme sample or prevalence estimate. "
         "Selected CHIP priorities are nutrition security, chronic-disease preventive services and substance-misuse/overdose prevention. "
         "Mobile screening in this plan concerns blood pressure, not Lyme. PathwayAI has no county or referral-platform partnership. "
         f"[Read the county plan]({CHIP_URL}) · [County assessment]({CHA_URL})")
