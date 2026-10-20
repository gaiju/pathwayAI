"""Reviewable chronology; quotations preserve uncertainty, not clinical interpretation."""
from report_download import branded_download_button
import re

VISIT_FIELDS = {
    "exposure": "Possible exposure: place and date",
    "tick": "Tick bite: what you observed",
    "removal": "When the tick was found or removed",
    "onset": "When symptoms began / time after exposure",
    "rash": "Rash or skin changes: appearance and timing",
    "symptoms": "Symptoms and how long they lasted",
    "tests": "Tests: name, date and reported result",
    "diagnosis": "Diagnosis date or delay, if reported",
    "care": "Care received and clinicians seen",
}


def story_details(story, details):
    # Source excerpts retain negation and relative dates; no disease/risk conclusion.
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", story) if p.strip()]
    def excerpts(pattern):
        return " ".join(p for p in parts if re.search(pattern, p, re.I))
    exposure = excerpts(r"\b(expos\w*|walk\w*|hik\w*|camp\w*|outdoors?)\b")
    if not exposure:
        exposure = "; ".join(str(v) for v in (details.get("exposure_location"), details.get("month")) if v)
    tests = excerpts(r"\b(test\w*|blood\s*(?:work|draw)|ELISA|immunoblot|western blot|PCR)\b")
    if not tests:
        tests = "; ".join(str(v) for v in (details.get("llm_test_status"), details.get("llm_test_result"), details.get("llm_test_timing")) if v)
    if not tests and details.get("tested"):
        tests = "Testing mentioned; name, date and result not reported."
    return {
        "exposure": exposure,
        "tick": excerpts(r"\b(tick|bitten|bite|biting)\b"),
        "removal": excerpts(r"\b(remov\w*|pull\w*|found|attach\w*)\b.*\btick\b|\btick\b.*\b(remov\w*|pull\w*|found|attach\w*)\b"),
        "onset": excerpts(r"\b(began|started|onset|developed|after|before|later)\b"),
        "rash": excerpts(r"\b(rash\w*|redness|red patch|bull.?s.?eye|erythema)\b"),
        "symptoms": excerpts(r"\b(symptom\w*|fever|fatigue|tired|pain|ache\w*|dizz\w*|headache\w*|numb\w*)\b") or ", ".join(details.get("symptoms") or []),
        "tests": tests,
        "diagnosis": excerpts(r"\b(diagnos\w*|confirmed)\b"),
        "care": excerpts(r"\b(doctor\w*|clinician\w*|provider\w*|hospital\w*|appointment\w*|treat\w*)\b") or
                (str(details["providers_seen"]) + " healthcare professionals reported" if details.get("providers_seen") is not None else ""),
    }


def visit_summary_text(story, details, reviewed_fields=None, reporter="Not reported"):
    facts = story_details(story, details) if reviewed_fields is None else reviewed_fields
    lines = ["PathwayAI | My visit summary", "Reported by: " + reporter,
             "Based on information entered by the user. Not independently verified. Patient/caregiver statements for review; not a diagnosis or test interpretation.",
             "", "EXPOSURE AND CARE TIMELINE"]
    lines += [label + ": " + (facts.get(key) or "Not reported") for key, label in VISIT_FIELDS.items()]
    lines += ["", "QUESTIONS TO CLARIFY", "- Are symptom duration and time to diagnosis different? Confirm what each time period describes.",
              "- Confirm missing dates, tick/removal details and rash timing; not reported does not mean No.",
              "- Bring the original laboratory report to confirm the test name, date and result.",
              "", "MY QUESTIONS AND CORRECTIONS", "Add your questions or corrections here.",
              "", "MY ORIGINAL NOTES (FOR CROSS-CHECKING)", story,
              "", "Bring a medication list if available. No dates or clinical conclusions have been inferred."]
    return "\n".join(lines)


def show_visit_summary(story, details):
    import streamlit as st
    reporter = st.session_state.get("reporter_role", "Not reported")
    fields_seed = story_details(story, details)
    field_source = (story, str(fields_seed))
    if st.session_state.get("visit_fields_source") != field_source:
        for key, value in fields_seed.items():
            st.session_state["visit_field_" + key] = value
        st.session_state["saved_visit_fields"] = dict(fields_seed)
        st.session_state["visit_fields_source"] = field_source
    st.markdown("### Your organized visit summary")
    st.write("Review the exposure-to-care timeline below. Keep positive or negative test results exactly as reported, and clarify dates you are unsure about.")
    with st.expander("Check or add bite, rash, symptom and test details"):
        st.write("These are your notes, not clinical findings. Keep a blank field if you do not know. A missing bite or rash does not rule out Lyme disease.")
        facts = {}
        for key, label in VISIT_FIELDS.items():
            widget = "visit_field_" + key
            if widget not in st.session_state:
                st.session_state[widget] = st.session_state.get("saved_visit_fields", fields_seed).get(key, "")
            facts[key] = st.text_input(label, key=widget, max_chars=5000)
        st.session_state["saved_visit_fields"] = facts
    seed = visit_summary_text(story, details, facts, reporter)
    if st.session_state.get("visit_summary_seed") != seed:
        st.session_state["visit_summary_seed"] = seed
        st.session_state["visit_summary_edit"] = seed
        st.session_state["visit_summary_reviewed"] = seed
    elif "visit_summary_edit" not in st.session_state:
        st.session_state["visit_summary_edit"] = st.session_state.get("visit_summary_reviewed", seed)
    edited = st.text_area("Review and edit your visit summary", key="visit_summary_edit", height=350, max_chars=60000)
    st.session_state["visit_summary_reviewed"] = edited
    branded_download_button("Download my visit summary", edited.encode("utf-8"),
                       file_name="PathwayAI_Visit_Summary.txt", mime="text/plain", key="visit_summary_download")
    st.caption("The timeline comes first; your original notes are retained at the end. Add costs and time below for a separate appointment and cost card.")
