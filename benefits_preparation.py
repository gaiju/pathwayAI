"""Preparation aid only: no applications, eligibility decisions or document uploads."""

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
        record = record or {}
        facts = []
        for key, label in (("period", "Recorded period"), ("reported_by", "Reported by"),
                           ("workdays", "Recorded workdays missed"), ("caregiver_hours", "Recorded unpaid help (hours)")):
            value = record.get(key)
            if value is not None and value not in ("", "Not reported"):
                facts.append(f"{label}: {value}")
        if facts:
            lines += ["", "OPTIONAL FACTS ALREADY IN YOUR PERSONAL RECORD (UNVERIFIED)", *facts,
                      "Review these entries. Your personal record does not replace agency forms or clinical evidence."]
    lines += ["", "QUESTIONS TO ASK", "- Which records and forms do you need?",
              "- How can I request communication or accessibility help?",
              "- What should I do if information is missing or a deadline is approaching?",
              "", "Official starting point: " + LINKS[program],
              "Keep Social Security numbers, bank details and identity documents out of PathwayAI."]
    return "\n".join(lines)


def show_benefits_preparation(record=None):
    import streamlit as st
    with st.expander("Prepare for a benefits conversation"):
        st.write("Reuse your personal record and a short checklist to prepare. Programs have different rules; an adviser or the agency can explain what applies.")
        program = st.selectbox("Which program do you want to discuss?", PROGRAMS, key="benefits_program")
        st.markdown(f"[Official {program} information]({LINKS[program]})")
        text = preparation_checklist(program, record)
        st.text(text)
        st.download_button("Download my preparation checklist", text.encode("utf-8"),
                           file_name="PathwayAI_Benefits_Preparation.txt", mime="text/plain",
                           key="benefits_checklist_download")
        st.caption("This tool organizes information. It does not determine eligibility, submit applications or guarantee benefits. Confirm requirements with the program or a qualified adviser.")
