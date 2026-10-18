"""Immediate, reviewable output from the existing story organizer."""


def visit_summary_text(story, details):
    fields = [
        ("Possible exposure location", details.get("exposure_location")),
        ("Approximate month reported", details.get("month")),
        ("Symptoms reported", ", ".join(details.get("symptoms") or [])),
        ("Duration reported", details.get("duration_text")),
        ("Healthcare professionals seen", details.get("providers_seen")),
        ("Testing", details.get("llm_test_status") or ("Testing mentioned; confirm details" if details.get("tested") else None)),
    ]
    lines = ["PathwayAI | My visit summary", "Personal notes for review; not a diagnosis.",
             "", "MY ORIGINAL NOTES", story, "", "ORGANIZED DETAILS"]
    lines.extend(f"{label}: {value if value not in (None, '') else 'Not reported'}" for label, value in fields)
    lines += ["", "QUESTIONS AND CORRECTIONS", "Add your questions or corrections here.",
              "", "Bring original test reports and a medication list if available."]
    return "\n".join(lines)


def show_visit_summary(story, details):
    import streamlit as st

    seed = visit_summary_text(story, details)
    if st.session_state.get("visit_summary_seed") != seed:
        st.session_state["visit_summary_seed"] = seed
        st.session_state["visit_summary_edit"] = seed
        st.session_state["visit_summary_reviewed"] = seed
    elif "visit_summary_edit" not in st.session_state:
        st.session_state["visit_summary_edit"] = st.session_state.get("visit_summary_reviewed", seed)
    st.markdown("### Your organized visit summary")
    st.write("Your summary is here. Check the details, add questions or corrections, then download it for your visit.")
    edited = st.text_area("Review and edit your visit summary", key="visit_summary_edit", height=300, max_chars=16000)
    st.session_state["visit_summary_reviewed"] = edited
    st.download_button("Download my visit summary", edited.encode("utf-8"),
                       file_name="PathwayAI_Visit_Summary.txt", mime="text/plain", key="visit_summary_download")
    st.caption("Your original notes are included so you can check what the organizer found. Add costs and time below if useful; the fuller appointment and cost card is a separate download.")
