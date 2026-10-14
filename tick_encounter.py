"""Optional encounter details reused across pages, private session only."""


def show_tick_encounter(existing=None):
    import streamlit as st

    existing = existing or {}
    saved = st.session_state.get("tick_encounter_record", {})
    fields = (
        ("when", "encounter_when", "When did you find the tick?", existing.get("month", "")),
        ("exposure", "encounter_exposure", "Where did you find it? ZIP or county and state", existing.get("exposure_location", "")),
        ("current", "encounter_current", "Where do you need care now? ZIP or county and state", existing.get("current_location", "")),
    )
    for field, key, label, suggested in fields:
        if key not in st.session_state:
            st.session_state[key] = saved.get(field, suggested) or ""
    with st.expander("Tick encounter details · optional, enter once"):
        st.write('Keep the details from your story. Add only what is missing. Where you found a tick may differ from where you are now.')
        for field, key, label, suggested in fields:
            st.text_input(label, key=key, max_chars=120,
                          help="A date or approximate month is fine; 'not sure' is also fine."
                          if field == "when" else "ZIP or county and state only; no street address needed.")
        st.write('These details stay in your session and summary. They are not shared automatically. Finding a tick does not confirm Lyme disease.')
    record = {field: st.session_state[key].strip() for field, key, _, _ in fields}
    record["evidence_type"] = "Patient-reported, unverified tick observation"
    st.session_state["tick_encounter_record"] = record
    return record
