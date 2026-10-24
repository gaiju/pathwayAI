"""Optional dated patient-reported observations: session only, never auto-summed."""
from datetime import date
import json
import math
from uuid import uuid4

HEADING = 'DATED DAILY-LIFE OBSERVATIONS'
PERIODS = ['Not reported', 'This day', 'Past 7 days', 'Past 30 days', 'Other — describe']
WORK = ['Not reported', 'No change', 'Missed work', 'Reduced hours', 'Changed duties', 'Stopped work', 'Not applicable']
ACTIVITIES = ['Walking', 'Household tasks', 'Driving', 'Childcare', 'Self-care', 'Social activities', 'Work or school', 'Other']


def normalize_observation(raw):
    observed = raw.get('date')
    if isinstance(observed, date):
        observed = observed.isoformat()
    if observed:
        date.fromisoformat(str(observed))
    hours = raw.get('caregiver_hours')
    if hours is not None:
        if isinstance(hours, bool) or not math.isfinite(float(hours)) or float(hours) < 0:
            raise ValueError('Caregiving hours must be a nonnegative number or left blank.')
        hours = float(hours)
    period = raw.get('period') or 'Not reported'
    work = raw.get('work_impact') or 'Not reported'
    if period not in PERIODS or work not in WORK:
        raise ValueError('Choose a listed period and work impact.')
    activities = list(raw.get('activities') or [])
    if any(value not in ACTIVITIES for value in activities):
        raise ValueError('Choose a listed activity.')
    return {'id': raw.get('id') or uuid4().hex, 'date': str(observed) if observed else None,
            'period': period, 'period_detail': str(raw.get('period_detail') or '').strip()[:200],
            'work_impact': work, 'activities': activities,
            'activity_note': str(raw.get('activity_note') or '').strip()[:1000],
            'caregiver_hours': hours, 'helper': str(raw.get('helper') or 'Not reported'),
            'support_needed': str(raw.get('support_needed') or '').strip()[:1000]}


def has_observation_content(row):
    return bool(row['date'] or row['period'] != 'Not reported' or row['work_impact'] != 'Not reported'
                or row['activities'] or row['activity_note'] or row['caregiver_hours'] is not None
                or row['helper'] != 'Not reported' or row['support_needed'])


def observation_rows(observations):
    result = []
    # Undated entries remain undated; dates are never inferred from reporting periods.
    ordered = sorted(enumerate(observations), key=lambda item: (item[1].get('date') is None, item[1].get('date') or '', item[0]))
    for _, raw in ordered:
        row = normalize_observation(raw)
        period = row['period']
        if period == 'Other — describe':
            period = row['period_detail'] or 'Other period — details not reported'
        activities = '; '.join(row['activities'])
        if row['activity_note']:
            activities = (activities + ': ' if activities else '') + row['activity_note']
        result.append({'Date': row['date'] or 'Not reported', 'Period': period,
                       'Work impact': row['work_impact'], 'Difficult activities': activities or 'Not reported',
                       'Caregiving hours': 'Not reported' if row['caregiver_hours'] is None else f"{row['caregiver_hours']:g}",
                       'Help provided by': row['helper'], 'Support needed': row['support_needed'] or 'Not reported'})
    return result


def observations_text(observations):
    if not observations:
        return ''
    lines = [HEADING, 'Patient/caregiver-reported observations for review.',
             'Periods may overlap. Entries are listed separately; do not add hours or dollars across observations.']
    for index, row in enumerate(observation_rows(observations), 1):
        lines += ['', f'Observation {index}'] + [f'{key}: {value}' for key, value in row.items()]
    return '\n'.join(lines)


def append_observations(text, observations, include=True):
    section = observations_text(observations) if include else ''
    return text + '\n\n' + section if section and HEADING not in text else text


def session_observations_text(text):
    import streamlit as st
    return append_observations(text, st.session_state.get('daily_life_observations', []),
                               st.session_state.get('include_daily_observations', st.session_state.get('saved_include_daily_observations', True)))


def _save_observation():
    import streamlit as st
    state = st.session_state
    raw = {field: state.get('observation_' + field) for field in
           ('date', 'period', 'period_detail', 'work_impact', 'activities', 'activity_note', 'caregiver_hours', 'helper', 'support_needed')}
    row = normalize_observation(raw)
    if not has_observation_content(row):
        state['observation_message'] = 'Add at least one detail, or leave this optional section empty.'
        return
    current = list(state.get('daily_life_observations', []))
    # Repeated identical submissions are not new observations.
    content = {k: v for k, v in row.items() if k != 'id'}
    if any({k: v for k, v in old.items() if k != 'id'} == content for old in current):
        state['observation_message'] = 'That observation is already in your record.'
        return
    if len(current) >= 100:
        state['observation_message'] = 'This session holds up to 100 observations. Download your record before starting a new session.'
        return
    state['daily_life_observations'] = current + [row]
    state['daily_observation_draft'] = {}
    state['observation_message'] = 'Observation added. Review the timeline below.'


def _remove_observation(observation_id):
    import streamlit as st
    st.session_state['daily_life_observations'] = [r for r in st.session_state.get('daily_life_observations', []) if r['id'] != observation_id]


def show_daily_observations():
    import streamlit as st
    draft = st.session_state.get('daily_observation_draft', {})
    defaults = {'date': None, 'period': 'Not reported', 'period_detail': '', 'work_impact': 'Not reported',
                'activities': [], 'activity_note': '', 'caregiver_hours': None, 'helper': 'Not reported', 'support_needed': ''}
    for field, default in defaults.items():
        key = 'observation_' + field
        if key not in st.session_state:
            value = draft.get(field, default)
            st.session_state[key] = date.fromisoformat(value) if field == 'date' and isinstance(value, str) else value
    with st.expander('Add a dated daily-life observation · optional'):
        st.write('Keep a short record for future visits or benefits conversations. All fields are optional. Use made-up information for pilot testing; leave out names and identifiers.')
        if st.session_state.get('observation_message'):
            st.info(st.session_state.pop('observation_message'))
        with st.form('daily_observation_form', clear_on_submit=True):
            st.date_input('Date of observation (optional)', value=None, key='observation_date')
            st.selectbox('Period covered by this observation', PERIODS, key='observation_period')
            st.text_input('If other, describe the period (optional)', key='observation_period_detail', max_chars=200)
            st.selectbox('Work impact during this period', WORK, key='observation_work_impact')
            st.multiselect('Activities that became difficult', ACTIVITIES, key='observation_activities')
            st.text_area('Daily-activity details (optional)', key='observation_activity_note', max_chars=1000, height=80)
            st.number_input('Unpaid caregiving hours for this observation (optional)', min_value=0.0, value=None, key='observation_caregiver_hours')
            st.selectbox('Who provided the unpaid help?', ['Not reported', 'Family or friend', 'Other unpaid helper'], key='observation_helper')
            st.text_input('What support would help next? (optional)', key='observation_support_needed', max_chars=1000)
            st.form_submit_button('Add observation to my record', key='add_daily_observation', on_click=_save_observation)
        st.session_state['daily_observation_draft'] = {field: st.session_state.get('observation_' + field) for field in defaults}
        observations = st.session_state.get('daily_life_observations', [])
        if observations:
            st.markdown('**Dated daily-life observations**')
            st.dataframe(observation_rows(observations), hide_index=True, use_container_width=True)
            st.write('Periods may overlap. Entries stay separate and do not change your spending or caregiving totals.')
            if 'include_daily_observations' not in st.session_state:
                st.session_state['include_daily_observations'] = st.session_state.get('saved_include_daily_observations', True)
            included = st.checkbox('Include these observations in my personal record downloads', key='include_daily_observations')
            st.session_state['saved_include_daily_observations'] = included
            from report_download import branded_download_button
            branded_download_button('Download my dated daily-life record', observations_text(observations).encode('utf-8'), file_name='PathwayAI_Dated_Daily_Life_Record.txt', mime='text/plain', key='daily_observations_download')
            options = {r['id']: f"{i+1}. {r.get('date') or 'Date not reported'} · {r['work_impact']}" for i, r in enumerate(observations)}
            remove = st.selectbox('Select an observation to remove', list(options), format_func=options.get, key='observation_remove_choice')
            st.button('Remove selected observation', key='remove_daily_observation', on_click=_remove_observation, args=(remove,))
        st.caption('Question topics informed by [Johnson et al. (2014)](https://doi.org/10.7717/peerj.322) and [Horn et al. (2025)](https://doi.org/10.3389/fmed.2025.1577936). These are custom preparation questions, not a validated disability scale.')
        st.caption('Stored only in this app session. Download to keep a copy; clearing the session removes the observations. They are not sent to AI or added to community evidence.')
    return list(st.session_state.get('daily_life_observations', []))
