"""Local support preparation; never sends records or determines eligibility."""
from report_download import branded_download_button

NEEDS = ("Disability benefits", "Paying for care", "Food or free meals",
         "Housing or rent support", "Temporary cash assistance", "Getting an appointment",
         "Getting to care", "Interpreter or accessibility help", "Utilities or heating help")


def support_summary(need, request, record=None, include_facts=False, reviewed_story=""):
    if need not in NEEDS and need != "Food or housing":
        raise ValueError("Unknown support need")
    record = record or {}
    lines = ["PathwayAI | My support summary", "Help needed: " + need, "", request]
    if include_facts:
        fields = [("period", "Time covered"), ("reported_by", "Recorded by")]
        if need == "Paying for care":
            fields += [("medical", "Money paid for care ($)"), ("other", "Other money paid ($)")]
        for key, label in fields:
            value = record.get(key)
            if value is not None and value not in ("", "Not reported"):
                lines.append(f"{label}: {value}")
        if need == "Paying for care" and record.get("bill"):
            lines += ["", "ONE BILL I CHOSE TO INCLUDE (NOT ADDED TO COST TOTALS)"]
            for label, value in record["bill"].items():
                if value not in (None, "", "Not reported"):
                    lines.append(f"{label}: {value}")
        if need == "Disability benefits":
            effects = record.get("daily_life_context", {}).get("person_daily_effects", [])
            if effects:
                lines += ["Reported daily-life effects: " + "; ".join(effects)]
            lines += ["Short-term costs or missed work do not establish disability eligibility. Ask about SSA's duration and other requirements; use the benefits checklist for a functional timeline."]
    if reviewed_story.strip():
        lines += ["", "DETAILS I CHOSE TO INCLUDE", reviewed_story.strip()]
    lines += ["", "Personal statements for review; not verified clinical evidence or a benefits application.",
              "Share only the details this service needs. Nothing is sent automatically."]
    return "\n".join(lines)


def show_support_summary(need, request, record=None):
    import streamlit as st
    with st.expander("Review and download a support summary"):
        st.write("Use what you already entered. Choose what to include, then check the summary before sharing.")
        context = dict(record or {})
        if need == "Paying for care":
            st.write("You can use your reviewed record to prepare for a conversation with an assistance organization about testing or treatment costs. Ask what documents it requires, whether applications are open, and which expenses it can cover. The organization decides eligibility; nothing is submitted through PathwayAI.")
            with st.expander("Add details of one bill (optional)"):
                st.write("Leave unknown amounts blank. These entries are not added to your spending totals. Do not enter account numbers, birth dates or other identifiers.")
                bill_keys = ("bill_organization", "bill_date", "bill_total", "bill_paid", "bill_balance", "bill_assistance")
                for key, value in st.session_state.get("saved_bill_details", {}).items():
                    if key not in st.session_state:
                        st.session_state[key] = value
                bill = {
                    "Billing organization": st.text_input("Hospital, clinic or laboratory name", key="bill_organization", max_chars=200),
                    "Bill date": st.text_input("Bill date (approximate is fine)", key="bill_date", max_chars=100),
                    "Bill total ($)": st.number_input("Total on this bill ($)", min_value=0.0, value=None, key="bill_total"),
                    "Paid toward this bill ($)": st.number_input("Already paid toward this bill ($)", min_value=0.0, value=None, key="bill_paid"),
                    "Balance stated on bill ($)": st.number_input("Unpaid balance stated on this bill ($)", min_value=0.0, value=None, key="bill_balance"),
                    "Financial-assistance status": st.selectbox("Financial-assistance application status", ["Not reported", "Not yet applied", "Pending", "Approved", "Denied", "Unsure"], key="bill_assistance"),
                }
                st.session_state["saved_bill_details"] = {key: st.session_state[key] for key in bill_keys}
                context["bill"] = bill
        include = st.checkbox("Include relevant cost or daily-life entries", value=False,
                              key="support_summary_facts", disabled=need not in ("Paying for care", "Disability benefits"))
        include_story = st.checkbox("Include my visit summary", value=False, key="support_summary_story")
        story = ""
        current = st.session_state.get("saved_story_text", "")
        if include_story:
            if st.session_state.get("notes_language", "English") != "English":
                source = st.session_state.get("translation_source")
                if (source and source[0] == current and source[1] == st.session_state.get("notes_language")
                        and source[2] == st.session_state.get("reporter_role")):
                    story = st.session_state.get("bilingual_reviewed", "")
            else:
                source = st.session_state.get("visit_fields_source")
                if source and source[0] == current:
                    story = st.session_state.get("visit_summary_reviewed", "")
            if not story:
                st.info("Organize your current notes first to include a reviewed visit summary. No old summary has been included.")
        seed = support_summary(need, request, context, include and need in ("Paying for care", "Disability benefits"), story)
        if include:
            from daily_observations import session_observations_text
            seed = session_observations_text(seed)
        if st.session_state.get("support_summary_seed") != seed:
            st.session_state["support_summary_text"] = seed
            st.session_state["support_summary_seed"] = seed
        reviewed = st.text_area("Keep only what you want to share", key="support_summary_text", height=180)
        branded_download_button("Download my support summary", reviewed.encode("utf-8"),
                           file_name="PathwayAI_Support_Summary.txt", mime="text/plain", key="support_summary_download")
        st.caption("Leave out Social Security numbers, bank details and identity documents. Your entries remain available during this session; download a copy to keep.")
