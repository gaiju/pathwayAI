"""Private, optional reporting context; not a validated proxy questionnaire."""

REPORTERS = ("Myself", "Myself, with help", "A caregiver, on someone else's behalf")


def show_reporter():
    import streamlit as st
    role = st.selectbox("Who is completing this record?", REPORTERS, index=REPORTERS.index(st.session_state.get("saved_reporter_role", REPORTERS[0])), key="reporter_role")
    st.session_state["saved_reporter_role"] = role
    if role == REPORTERS[2]:
        st.caption("Describe the person receiving care. Keep your own experience separate below. Share only with appropriate permission.")
    return role


def show_daily_life():
    import streamlit as st
    saved = st.session_state.get("saved_daily_life_context", {})
    for key, default in (("person_daily_effects", []), ("caregiver_own_experience", "")):
        if key not in st.session_state:
            st.session_state[key] = saved.get(key, default)
    with st.expander("Daily life and caregiver experience · optional"):
        st.multiselect("What has become harder for the person receiving care?", [
            "Washing, dressing or using the toilet", "Speaking or communicating",
            "Reading, screens or concentration", "Work or school",
            "Seeing family or friends", "Taking part in important life events",
        ], key="person_daily_effects")
        st.text_area("Caregiver's own experience, in their own words (optional)",
                     key="caregiver_own_experience", max_chars=1200, height=80,
                     placeholder="For example: changes to your work, rest or family life. Leave out identifying details.")
        st.caption("Add only what you know. Partial answers are fine. These details stay in this session and your personal download.")
    record = {"person_daily_effects": list(st.session_state["person_daily_effects"]),
              "caregiver_own_experience": st.session_state["caregiver_own_experience"]}
    st.session_state["saved_daily_life_context"] = record
    return record


def reporting_lines(role, context=None):
    lines = ["REPORTED BY: " + role]
    if role == REPORTERS[2]:
        lines.append("Caregiver observations; not assumed to be the person's own report or a clinically verified assessment.")
    context = context or {}
    if context.get("person_daily_effects"):
        lines += ["DAILY-LIFE EFFECTS FOR THE PERSON RECEIVING CARE", "; ".join(context["person_daily_effects"])]
    if context.get("caregiver_own_experience"):
        lines += ["CAREGIVER'S OWN EXPERIENCE", context["caregiver_own_experience"]]
    return lines
