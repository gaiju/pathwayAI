"""Public evidence and nonclinical actions; never reads patient session records."""
from functools import lru_cache
from pathlib import Path
import math
import zipfile
from mid_hudson_counties import COUNTIES

BASE = Path(__file__).resolve().parent
HRSA_URL = 'https://data.hrsa.gov/topics/health-workforce/nchwa/ahrf'
CDC_URL = 'https://www.cdc.gov/lyme/data-research/facts-stats/index.html'
AUDIENCE_ACTIONS = {
    'Public health departments': (
        'Share tick-prevention information through local events and trusted community channels.',
        'Review county surveillance alongside service availability; ask residents which barriers need attention.',
        'Bring residents and potential partners together to choose one support priority and agree how to follow up.',
    ),
    'Clinics and community health centers': (
        'Make prevention information and visit-preparation tools easy to find before an appointment.',
        'Help people ask about appointment availability, interpreter services, income-based fees and financial assistance.',
        'Offer a way to review patient-prepared notes and connect people with existing transport or support resources.',
    ),
    'Patient advocacy organizations': (
        'Help patients and caregivers prepare a record of spending, missed work, unpaid care and daily-life impacts.',
        'Review language and accessibility barriers with residents, including people who need help using digital tools.',
        'Share verified support resources and help residents shape community planning priorities without requiring personal data sharing.',
    ),
}
ACTION_AREAS = (
    ('Prevention education and tick-bite awareness', 'Share established prevention information through trusted local channels.'),
    ('Timely access to healthcare', 'Help residents find care and ask about appointments, costs, transport and interpreters.'),
    ('Financial and caregiving burden', 'Recognize spending, missed work, unpaid care and support needs beyond medical bills.'),
    ('Language access and community resources', 'Make information easier to understand and connect residents with existing local support.'),
)
EVIDENCE_TYPES = (
    ('Observed public health data', 'NYSDOH 2024 reported county cases and rates; CDC historical county files cover 2019–2022. These years are separate, not a combined current feed.'),
    ('Published research estimates', 'Hook et al. measured medical, nonmedical and productivity costs in a selected study population. County calculations are illustrations in 2016 dollars, not measured local spending.'),
    ('Patient survey findings', 'PathwayAI’s supplied October 3, 2026 snapshot describes 33 respondents reporting a Lyme diagnosis. It is a small, self-selected sample across locations, not representative of a county or the U.S. population.'),
    ('Suggested actions', 'Discussion options for residents and partners to review. They are not adopted programs, clinical recommendations or demonstrated savings.'),
)
SURVEY_CONTEXT = {
    'evidence_type': 'Patient survey findings',
    'snapshot_date': '2026-10-03',
    'sample_size': 33,
    'sampling': 'Small, self-selected sample across locations; respondents self-reported a Lyme diagnosis.',
    'themes': 'The supplied summary raises questions about spending, time lost, repeated visits and diagnosis delays.',
    'limits': 'Not representative of the selected county or the U.S. population. Raw responses, question-specific denominators and cost/time reporting periods have not been verified here; no survey percentages or county totals are calculated.',
    'source': 'Project-lead-supplied summary already documented in the app; not a new analysis of raw responses.',
    'privacy': 'Only this aggregate context is included. Personal app entries are not included in community evidence.',
}


def audience_actions(audience):
    if audience not in AUDIENCE_ACTIONS:
        raise ValueError('Choose a supported community audience.')
    return list(AUDIENCE_ACTIONS[audience])


def _nonnegative(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result >= 0 else None


@lru_cache(maxsize=16)
def healthcare_context(county, asset_path=None):
    """Read existing AHRF fields by county FIPS; missing values stay unavailable."""
    fips = COUNTIES
    if county not in fips:
        raise ValueError('Unsupported county.')
    fields = {'Primary-care physicians': 'phys_nf_prim_care_pc_exc_rsdt_23',
              'Hospitals': 'hosp_23', 'Hospital beds': 'hosp_beds_23'}
    result = {'county': county, 'fips': fips[county], 'year': 2023,
              'release': 'AHRF 2024–2025', 'source_url': HRSA_URL,
              'indicators': {label: None for label in fields},
              'status': 'Source unavailable; no values substituted.',
              'limits': 'General healthcare resource context, not Lyme expertise, appointment availability, interpreter access or a verified shortage.'}
    try:
        import pandas as pd
        with zipfile.ZipFile(asset_path or BASE / 'AHRF_2024-2025_CSV.zip') as archive:
            name = next(n for n in archive.namelist() if n.endswith('AHRF2025.csv'))
            frame = pd.read_csv(archive.open(name), usecols=['fips_st_cnty', *fields.values()], dtype={'fips_st_cnty': str})
        rows = frame[frame['fips_st_cnty'].str.zfill(5) == fips[county]]
        if len(rows) == 1:
            result['indicators'] = {label: _nonnegative(rows.iloc[0][field]) for label, field in fields.items()}
            result['status'] = 'Existing public AHRF asset; 2023 county fields.'
    except (OSError, ValueError, KeyError, StopIteration, zipfile.BadZipFile):
        pass
    return result


def show_community_action_summary():
    import streamlit as st
    with st.container(key='community_action_summary'):
        st.subheader('From Lyme Disease Burden to Community Action')
        st.write('Explore county evidence, choose a support priority, and download a planning brief.')
        st.markdown('**Four support areas to consider**')
        display_areas = (
            ('Prevention', 'Share tick-prevention information.'),
            ('Access to care', 'Explore appointments, transport and affordability.'),
            ('Costs and caregiving', 'Recognize missed work, unpaid care and support needs.'),
            ('Language and local support', 'Make information and resources easier to access.'),
        )
        for start in range(0, len(display_areas), 2):
            for column, (title, description) in zip(st.columns(2), display_areas[start:start + 2]):
                with column:
                    st.markdown('**' + title + '**')
                    st.write(description)
        audience = st.selectbox('Choose your organization type', list(AUDIENCE_ACTIONS), key='community_action_audience')
        st.markdown('**Actions to discuss**')
        for action in audience_actions(audience):
            st.markdown('- ' + action)
        st.markdown('**Next:** Open **Plan community support**, choose a county and support priority, then download the brief.')
        st.caption('Suggestions appear in your county brief. No personal information is needed here.')
        with st.expander('How the evidence fits together'):
            st.write('CDC and NYSDOH describe surveillance patterns; HRSA provides healthcare-resource context; patient-reported experiences identify burdens to investigate; published research provides cost estimates with defined populations and years.')
            for title, description in EVIDENCE_TYPES:
                st.markdown('**' + title + '**')
                st.write(description)
            st.write('The survey can guide questions, not county estimates. Its question-level denominators and reporting periods still need verification. HRSA resource counts do not confirm that a service is accessible to a particular resident.')
            st.markdown(f'[CDC surveillance context]({CDC_URL}) · [HRSA AHRF]({HRSA_URL})')
    return audience
