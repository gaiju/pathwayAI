"""Preparation aid only: no applications, eligibility decisions or document uploads."""
from report_download import branded_download_button

PROGRAMS = ("SSI", "SSDI", "SNAP / food assistance")
LINKS = {
    "SSI": "https://www.ssa.gov/ssi/",
    "SSDI": "https://www.ssa.gov/disability/",
    "SNAP / food assistance": "https://www.fns.usda.gov/snap/state-directory",
}


def preparation_checklist(program, record=None):
    if program not in PROGRAMS:
        raise ValueError("Unknown program")
    lines = ["PathwayAI | Prepare for a benefits conversation", "Program: " + program,
             "Preparation aid, not an application, medical opinion or eligibility decision.",
             "Ask the program or a qualified adviser which documents apply to you.", ""]
    if program == "SNAP / food assistance":
        lines += ["ASK YOUR STATE PROGRAM ABOUT:",
                  "- Household members and how the program defines your household.",
                  "- Income and expenses the program asks you to document.",
                  "- Application steps, deadlines and available interview assistance.",
                  "- Interpreter, accessibility or authorized-representative arrangements.",
                  "Provide medical details only if the program specifically needs them."]
    else:
        lines += ["ORGANIZE EXISTING INFORMATION:",
                  "- Symptoms, approximate dates, and changes over time.",
                  "- Effects on daily activities and work, including how often help is needed.",
                  "- Relevant clinician contacts, visits, test reports and treatment records.",
                  "- Work history and changes in hours or duties.",
                  "- Separate patient statements from caregiver observations.",
                  "Ask which additional financial documents apply to SSI." if program == "SSI" else "Ask how your work and earnings history relates to SSDI requirements."]
        lines += ["", "UNDERSTAND THE ADULT DISABILITY STANDARD",
                  "For adult disability-based SSI/SSDI, SSA generally requires a medically determinable condition preventing substantial gainful activity that has lasted or is expected to last at least 12 months, or result in death.",
                  "Short-term missed work or caregiver hours alone do not establish this. Other medical, work-history and financial rules apply. SSI also has aged/blind eligibility routes; ask which rules apply.",
                  "", "PREPARE A FUNCTIONAL TIMELINE",
                  "- What could you do before, and what is difficult now? Describe specific activities.",
                  "- When did each limitation begin, how often does it occur, and what help is needed?",
                  "- Which existing clinical records document changes over time?",
                  "- Ask your clinician about expected duration; do not infer it from a short reporting window."]
        if (record or {}).get("tick_related_preparation"):
            lines += ["", "IF YOU ARE PREPARING BECAUSE OF LYME OR ANOTHER TICK-RELATED CONDITION",
                      "- Separate your reported condition from any diagnosis documented by a clinician; do not infer a diagnosis from symptoms.",
                      "- Record exposure, symptom onset, diagnosis and treatment dates separately; mark unknown dates as unknown.",
                      "- Keep original test reports, treatment records and clinician assessments. PathwayAI does not interpret tests.",
                      "- Describe specific work and daily-life limitations, their frequency, fluctuations, help needed and expected duration if documented.",
                      "- Describe other health conditions that may affect function; do not automatically attribute every limitation to Lyme.",
                      "- Ask a clinician or qualified adviser which evidence is needed. A Lyme diagnosis alone does not establish eligibility."]
        history = (record or {}).get("functional_history", "")
        if history:
            lines += ["", "FUNCTIONAL CHANGES I CHOSE TO INCLUDE (UNVERIFIED)", history]
    if program != "SNAP / food assistance":
        lines += ["", "FIND THE RIGHT APPLICATION ROUTE",
                  "SSDI and SSI are federal programs, not separate Lyme application forms for each state.",
                  "Ask SSA or an adviser about the Adult Disability Report (SSA-3368), Function Report - Adult (SSA-3373), and any forms requested for your own claim. Not everyone needs the same forms or application route.",
                  "Official SSA forms directory: https://www.ssa.gov/forms/",
                  "Find a Social Security office: https://www.ssa.gov/locator/",
                  "State short-term disability, paid medical leave, employer insurance and workers' compensation are different programs. Availability and eligibility vary; the relevant state may depend on where you work, not only where you live.",
                  "Confirm current forms, deadlines and filing instructions with the program. PathwayAI has not verified a 50-state application directory."]
    lines += ["", "QUESTIONS TO ASK", "- Which records and forms do you need?",
              "- How can I request communication or accessibility help?",
              "- What should I do if information is missing or a deadline is approaching?",
              "", "Official starting point: " + LINKS[program],
              "Keep Social Security numbers, bank details and identity documents out of PathwayAI."]
    return "\n".join(lines)


def show_benefits_preparation(record=None):
    import streamlit as st
    with st.expander("Prepare for a benefits conversation"):
        st.write("Prepare a program-specific checklist and questions. For disability benefits, describe changes in function over time. An adviser or the agency can explain which rules apply.")
        program = st.selectbox("Which program do you want to discuss?", PROGRAMS, key="benefits_program")
        st.markdown(f"[Official {program} information]({LINKS[program]})")
        context = dict(record or {})
        if program != "SNAP / food assistance":
            st.write("A few missed workdays do not establish disability-benefit eligibility. Prepare a timeline of limitations over time and discuss the rules with an adviser.")
            if "benefits_functional_history" not in st.session_state:
                st.session_state["benefits_functional_history"] = st.session_state.get("saved_benefits_functional_history", "")
            st.write("SSDI and SSI use federal application routes. State short-term disability and paid medical leave are separate programs; ask which rules apply where you work.")
            st.markdown("[Official SSA forms directory](https://www.ssa.gov/forms/) · [Find a Social Security office](https://www.ssa.gov/locator/)")
            context["tick_related_preparation"] = st.checkbox("Include Lyme / tick-related preparation questions", key="benefits_tick_related")
            history = st.text_area("Functional changes over time (optional)", key="benefits_functional_history",
                                   placeholder="Approximate date; activity before and now; frequency; help needed. Leave out identifiers.", max_chars=4000)
            st.session_state["saved_benefits_functional_history"] = history
            context["functional_history"] = history
        text = preparation_checklist(program, context)
        st.text(text)
        branded_download_button("Download my preparation checklist", text.encode("utf-8"),
                           file_name="PathwayAI_Benefits_Preparation.txt", mime="text/plain",
                           key="benefits_checklist_download")
        st.caption("This tool organizes information. It does not determine eligibility, submit applications or guarantee benefits. Confirm requirements with the program or a qualified adviser.")
