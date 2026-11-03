"""Public-only pathway display and descriptive, source-linked planning prompts."""
from html import escape

PATIENT_STEPS = ('Prevent', 'Prepare for care', 'Record burden', 'Find support')
COMMUNITY_STEPS = ('Compare county evidence', 'Choose a support priority', 'Download a brief', 'Review locally')


def show_pathway():
    import streamlit as st
    st.markdown('**Two connected pathways**')
    for title, steps in [('For patients and caregivers', PATIENT_STEPS), ('For community teams', COMMUNITY_STEPS)]:
        items=''.join('<span style="border:1px solid currentColor;border-radius:6px;padding:6px 10px;">'+str(i)+'. '+escape(step)+'</span>' for i,step in enumerate(steps,1))
        st.markdown('<div style="margin:8px 0 12px;"><strong>'+title+'</strong><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:7px;">'+items+'</div></div>',unsafe_allow_html=True)
    st.caption('Personal records remain separate from county evidence. Community planning uses public data and clearly labeled research illustrations.')


def local_planning_notes(report):
    county=report['county'];rate=report['reported_rate_per_100000'];state=report['state_reported_rate_per_100000']
    rate_source=next(x for x in report['sources'] if x['purpose']=='Reported rates per 100,000')
    if rate is None or state is None:
        comparison='A comparable county/state rate is unavailable; no relative rate is inferred.'
    else:
        direction='above' if rate>state else 'below' if rate<state else 'equal to'
        comparison=f"{county}'s 2024 reported rate was {rate:g} per 100,000, {direction} the state rate of {state:g}. Where could trusted local channels help share prevention information?"
    notes=[{'title':'Prevention outreach','text':comparison,'source_url':rate_source['url'],'period':'NYSDOH 2024'}]
    rows=report['additional_public_context']['socioeconomic_context']
    uninsured=next((x for x in rows if x['field']=='pers_noins_lt65_pct_22'),None)
    if uninsured and uninsured['value'] is not None:
        text=f"{uninsured['value']:g}% of residents under age 65 were uninsured in {uninsured['year']}. Could care navigators help residents ask about sliding fees and coverage options?"
    else:
        text='The under-65 uninsured estimate is unavailable. Ask local partners what verified information could help assess access barriers.'
    notes.append({'title':'Care access','text':text+' This is general population context, not Lyme-specific need or available appointments.','source_url':next(x['url'] for x in report['sources'] if 'Healthcare resources' in x['purpose']),'period':'HRSA AHRF · insurance 2022'})
    notes.append({'title':'A question for local review','text':report['planning']['decision']+' Confirm needs with residents and check existing services before selecting a response.','source_url':None,'period':'Suggested planning question, not a local finding'})
    return notes
