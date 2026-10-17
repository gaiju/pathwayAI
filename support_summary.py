"""Local support preparation; never sends records or determines eligibility."""

NEEDS = ("Paying for care", "Getting an appointment", "Getting to care",
         "Interpreter or accessibility help", "Food or housing", "Disability benefits")


def support_summary(need, request, record=None, include_facts=False, reviewed_story=""):
    if need not in NEEDS:
        raise ValueError("Unknown support need")
    record = record or {}
    lines = ["PathwayAI | My support summary", "Help needed: " + need, "", request]
    if include_facts:
        fields = [("period", "Time covered"), ("reported_by", "Recorded by")]
        if need == "Paying for care":
            fields += [("medical", "Money paid for care ($)"), ("other", "Other money paid ($)")]
        elif need == "Disability benefits":
            fields += [("workdays", "Workdays missed"), ("caregiver_hours", "Unpaid help (hours)")]
        for key, label in fields:
            value = record.get(key)
            if value is not None and value not in ("", "Not reported"):
                lines.append(f"{label}: {value}")
        if need == "Disability benefits":
            effects = record.get("daily_life_context", {}).get("person_daily_effects", [])
            if effects:
                lines += ["Reported daily-life effects: " + "; ".join(effects)]
    if reviewed_story.strip():
        lines += ["", "DETAILS I CHOSE TO INCLUDE", reviewed_story.strip()]
    lines += ["", "Personal statements for review; not verified clinical evidence or a benefits application.",
              "Share only the details this service needs. Nothing is sent automatically."]
    return "\n".join(lines)


def show_support_summary(need, request, record=None):
    import streamlit as st
    with st.expander("Review and download a support summary"):
        st.write("Use what you already entered. Choose what to include, then check the summary before sharing.")
        include = st.checkbox("Include relevant cost or daily-life entries", value=False,
                              key="support_summary_facts", disabled=need not in ("Paying for care", "Disability benefits"))
        include_story = st.checkbox("Include my visit summary", value=False, key="support_summary_story")
        story = st.session_state.get("summary88_text", "") if include_story else ""
        seed = support_summary(need, request, record, include and need in ("Paying for care", "Disability benefits"), story)
        if st.session_state.get("support_summary_seed") != seed:
            st.session_state["support_summary_text"] = seed
            st.session_state["support_summary_seed"] = seed
        reviewed = st.text_area("Keep only what you want to share", key="support_summary_text", height=180)
        st.download_button("Download my support summary", reviewed.encode("utf-8"),
                           file_name="PathwayAI_Support_Summary.txt", mime="text/plain", key="support_summary_download")
        st.caption("Leave out Social Security numbers, bank details and identity documents. Your entries remain available during this session; download a copy to keep.")
