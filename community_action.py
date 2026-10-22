"""Fictional participation demonstration and human-reviewed community planning."""
from report_download import branded_download_button
from burden_demo import aggregate_demo, fictional_cards, show_burden_pathway_demo


ACTION_OPTIONS = {
    "Care without insurance and medical bills": {
        "decision": "Could existing services meet reported uninsured-care needs, or would an additional funded response be needed?",
        "need": "Uninsured care, unaffordable bills and difficulty reaching financial assistance",
        "context": "County insurance and healthcare-capacity measures provide context, not individual eligibility, available appointments or a Lyme-specific unmet-need count.",
        "action": "Review health-center sliding-fee access, coverage enrollment help and hospital financial assistance with patients; identify staffing, appointment capacity, costs and a possible funding source before proposing new services.",
        "participants": "Patients, health centers, hospital financial-assistance staff, enrollment assisters, county planners and potential funders",
        "measure": "Care appointments reached; enrollment assistance completed; financial-assistance decisions; remaining bills and unmet needs over a common period",
    },
    "Getting to care": {
        "decision": "Should a county care-navigation team investigate a small ride-navigation pilot with willing residents?",
        "need": "Travel, appointment and referral barriers",
        "context": "Compare reported Lyme rates and general HRSA capacity; neither measures travel barriers or available appointments.",
        "action": "Ask willing residents and transport providers to review ride eligibility, accessibility and appointment coordination.",
        "participants": "Patient and caregiver representatives, transport services and care navigators",
        "measure": "Requested and completed accessible rides; appointments attended; travel spending; support still needed",
    },
    "Unpaid care and daily life": {
        "decision": "Which practical-care or respite gap should a community support team investigate first?",
        "need": "Help with daily tasks, lost rest and caregiver time",
        "context": "General disability context can inform accessible planning; it is not Lyme disability prevalence or a measure of caregiver demand.",
        "action": "Review respite and practical assistance options with people receiving care and caregivers, recording their experiences separately.",
        "participants": "Patients, caregivers, disability organizations and social-care teams",
        "measure": "Caregiver hours over the same period; assistance requested and received; unmet daily-life needs",
    },
    "Food, housing and benefits": {
        "decision": "Should a community benefits-navigation team test assisted paperwork and follow-up?",
        "need": "Difficulty completing paperwork or reaching essential support",
        "context": "County context describes populations; individual needs and benefit eligibility must be checked separately.",
        "action": "Discuss assisted applications, accessible communication and follow-up with 211 and qualified benefits advisers.",
        "participants": "Patients, caregivers, benefits advisers and community support organizations",
        "measure": "Requests made; application assistance completed; referrals completed; needs still unmet",
    },
    "Work, school and relationships": {
        "decision": "Which accessibility or participation support should community partners explore with participants?",
        "need": "Lost work or school time, isolation and missed life events",
        "context": "Claims and disease reports do not measure all lost opportunities or social participation. No local demand estimate is available here.",
        "action": "Ask participants which work, school, accessibility or social-connection supports would be useful; review feasible responses with partners.",
        "participants": "Patients, caregivers, community organizations and appropriate work or school support teams",
        "measure": "Days missed in a common period; support requested and received; participant-described participation",
    },
}


def pathway_evidence():
    return [
        {"Layer": "Reported Lyme context", "Source": "NYSDOH 2024 county cases and rates PDFs, page 5; checked against supplied PDFs",
         "Period": "2024", "Type": "Public surveillance reports", "Scope": "County residents; not all infections, individual exposure or unmet support demand",
         "Reference": "https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf"},
        {"Layer": "General healthcare capacity", "Source": "HRSA AHRF 2024–2025 release, local county file",
         "Period": "2023 fields", "Type": "Public county resource context", "Scope": "General physicians, hospitals and beds; not Lyme expertise, wait times or appointment access",
         "Reference": "https://data.hrsa.gov/topics/health-workforce/nchwa/ahrf"},
        {"Layer": "Comparable participant summary example", "Source": "Six authored fictional cards in burden_demo.py; not collected or derived from a research dataset",
         "Period": "Invented past-30-days reporting window; before diagnosis", "Type": "Synthetic demonstration", "Scope": "Dutchess residence only; no real participants or county prevalence estimate",
         "Reference": "Local authored demonstration"},
        {"Layer": "Travel-cost scenario", "Source": "User-selected round-trip count and assumed price",
         "Period": "One invented person's next 30 days", "Type": "Assumption-based calculation", "Scope": "Trips × price; no price verification, county extrapolation or causal savings",
         "Reference": "Editable assumptions in this page"},
    ]


def action_brief(need):
    plan = ACTION_OPTIONS[need]
    rows = {r["Measure"]: r for r in aggregate_demo(fictional_cards())}
    lines = [
        "PathwayAI | Patient voice to community action",
        "PLANNING DEMONSTRATION — not a real patient aggregate or an adopted county program",
        "SELECTED PLANNING THEME: " + need,
        "DECISION TO EXPLORE: " + plan["decision"],
        "NEED TO REVIEW: " + plan["need"],
        "COUNTY CONTEXT: " + plan["context"],
        "PROPOSED ACTION: " + plan["action"],
        "POTENTIAL PARTICIPANTS (NOT COMMITTED PARTNERS): " + plan["participants"],
        "MEASURES TO AGREE WITH PARTICIPANTS: " + plan["measure"],
        "", "SEPARATE SYNTHETIC EXAMPLE",
        "Six invented Dutchess-residence cards; past 30 days; before diagnosis. Not collected reports.",
        "Care barrier: " + rows["Care barrier"]["Synthetic result"],
        "Median missed workdays: " + rows["Median missed workdays"]["Synthetic result"],
        "Median caregiver hours: " + rows["Median unpaid caregiver hours"]["Synthetic result"],
        "Five usable answers for each displayed measure; one missing. Selecting a planning theme does not create reports for that theme.",
        "", "RESOURCES AND FUNDING",
        "Check existing service capacity, staff time, estimated cost, a possible funding source and a responsible partner. If resources are unavailable, record the need as unmet rather than promise a referral will solve it.",
        "An appropriately sourced brief could support a county budget discussion or grant proposal. It does not secure funding, establish a county duty to pay, or demonstrate clinical benefit or cost savings.",
        "", "HUMAN REVIEW AND EVALUATION",
        "Patients and caregivers review needs; partners check feasibility and agree responsibilities, follow-up and measures before action.",
        "Compare the same reporting period and report missing answers and who could not participate. Before/after differences alone do not establish an effect.",
        "Needs can change from week to week. Repeated reviewed records would be needed to understand change; this demonstration does not store longitudinal observations.",
        "Real voluntary aggregates describe contributors, not all county residents. Small-group suppression alone does not ensure privacy or statistical reliability.",
        "No patient session entries, raw stories or real contributions are included in this demonstration or download.",
    ]
    lines.extend(["", "PROVENANCE: SOURCE, PERIOD, TYPE AND SCOPE"])
    for evidence in pathway_evidence():
        lines.append(" | ".join(f"{key}: {value}" for key, value in evidence.items()))
    return "\n".join(lines)


def scenario_cost(trips, cost_per_trip):
    """Explicit user assumptions, without a clinical or savings inference."""
    return trips * cost_per_trip


def show_community_action_pathway(simple=True):
    import streamlit as st

    st.markdown("### Patient Voices → Community Action")
    st.write("For county and community teams: turn a support priority into a practical plan to review with patients and caregivers.")
    st.markdown("**What you can do here**\n\n- Choose a support priority to discuss with patients and caregivers.\n- Explore a possible response and identify potential partners.\n- Download a planning brief for a team discussion or grant proposal.\n- Choose measures to track support received and needs still unmet.")
    st.caption("Planning tool · Proposed actions for partner review")
    need = st.selectbox("Choose a support priority", list(ACTION_OPTIONS), key="community_action_need")
    plan = ACTION_OPTIONS[need]
    with st.container(border=True):
        st.markdown("**1. Understand the need**")
        st.write(plan["need"] + ".")
        st.markdown("**2. Review a possible response**")
        st.write(plan["action"])
        st.markdown("**3. Bring the right partners together**")
        st.write(plan["participants"] + ".")
        st.markdown("**4. Agree on follow-up**")
        st.write(plan["measure"] + ".")
    branded_download_button("Download this action brief", action_brief(need).encode("utf-8"),
                       file_name="PathwayAI_Planning_Demonstration.txt", mime="text/plain", key="voice_action_brief")
    with st.expander("Review feasibility and responsibilities"):
        st.write("**Planning question:** " + plan["decision"])
        st.write("**County context:** " + plan["context"])
        st.write("Before proposing a service, check appointments, staff time, costs, funding and a responsible partner. Record needs that existing services cannot meet.")
        st.write("Review priorities with patients and caregivers. Agree on a common reporting period and repeated check-ins to track changing needs.")
        st.write("The brief can support a budget discussion or grant proposal. Services and funding require partner agreement. Health improvements and savings would need evaluation.")
    with st.expander("Evidence behind this pathway: sources, periods and limits"):
        st.dataframe(pathway_evidence(), hide_index=True, use_container_width=True)
        st.write("Patient reports, clinical records, surveillance and modeled results answer different questions. Relevance, collection method and reliability matter; a source label alone does not validate a claim.")
    with st.expander("See how comparable patient reports could be summarized"):
        show_burden_pathway_demo(simple=simple)
        st.write("For real contributions: ask permission, use residence and common periods, check duplicates and missing answers, and review disclosure risk. Summaries describe contributors, not county prevalence. People too ill to respond need accessible participation and appropriately authorized caregiver options.")
    with st.expander("Explore an assumed travel-cost scenario"):
        st.write("**ASSUMPTIONS — one invented person's next 30 days, not observed spending or a service-price quote.**")
        trips = st.number_input("Assumed round trips in 30 days", min_value=0, max_value=100, value=3, step=1, key="action_trips")
        cost = st.number_input("Assumed money paid per round trip ($)", min_value=0.0, max_value=10000.0, value=15.0, step=1.0, key="action_trip_cost")
        amount = scenario_cost(trips, cost)
        st.metric("Illustrative travel spending for one person", f"${amount:,.2f}")
        st.write(f"{trips} round trips × ${cost:,.2f} = ${amount:,.2f}. Change the assumptions to explore a different situation.")
        st.caption("Not added to patient records, published societal costs or county totals. No county demand, benefit or savings is inferred.")
    return action_brief(need)
