"""Four-part provenance for transferred county cost illustrations, not new arithmetic."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
CASE_SOURCE = 'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf'
HOOK_SOURCE = 'https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article'
YU_SOURCE = 'https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880'
FIPS = {'Dutchess': '36027', 'Orange': '36071'}
LABELS = [('reported_cases_context', 'Reported cases'), ('published_cost_context', 'Published cost'),
          ('calculation_assumptions', 'Calculation assumptions'), ('additional_burden_to_measure', 'Additional burden to measure')]


def explanation_fields(county, cases, unit, dollar_year, perspective, assumed_share=None):
    societal = str(perspective).lower().startswith('societal')
    if societal:
        hook = json.loads((BASE / 'data/hook_2022_article_verification.json').read_text())
        population = f"Hook et al. (2022): societal analysis n={hook['societal_analysis_n']}; reported cases in four high-incidence U.S. states; recruitment 2014–2016"
        scope = 'medical, nonmedical and productivity costs'
        evidence = 'data/hook_2022_article_verification.json'
        cost_url = HOOK_SOURCE
    else:
        population = 'Yu et al. (2026): inherited medical-episode reference; original study table and population details still require verification'
        scope = 'direct medical episode spending; patient payments are a component, not an addition'
        evidence = 'Inherited Yu reference in app.py/county_cost_scenario.py; original-table verification pending'
        cost_url = YU_SOURCE
    case_mix = ('No local case-mix adjustment.' if assumed_share is None else
                f'User-selected disseminated share {assumed_share:.0%}; not an observed county distribution.')
    return {
        'reported_cases_context': f'{county}, New York; FIPS {FIPS.get(county, "not reported")}; {int(cases):,} reported resident cases in 2024. Source: {CASE_SOURCE}',
        'published_cost_context': f'USD {unit:,.2f} per participant/episode, {dollar_year} dollars; {scope}. {population}. Source: {cost_url}',
        'calculation_assumptions': f'Reported cases × selected published unit cost. Transfer of study experience to the county is assumed. No underreporting or inflation adjustment. {case_mix} Populations and periods differ. Keep medical, household and societal perspectives separate; do not add Yu and Hook totals or interpret their difference as savings.',
        'additional_burden_to_measure': 'Complete pre-diagnosis history; continuing costs and disability beyond the study horizon; separately measured caregiver time and valuation; and effects in populations excluded from the source. Some components are already included in a societal mean: identify overlap before adding any new cost.',
        'provenance': f'Cases: data/ny_lyme_cases_2024_verification.json, supplied NYSDOH PDF page 5. Costs: {evidence}. See docs/burden_methodology.md; framework version 0.2.0.',
    }


def explanation_text(row):
    return '\n'.join(['STUDY-BASED COUNTY BURDEN ILLUSTRATION'] +
                     [label.upper() + ': ' + row[key] for key, label in LABELS] + ['PROVENANCE: ' + row['provenance']])


def show_county_explanation(rows, key):
    import streamlit as st
    with st.expander('How this county illustration is built'):
        selected = st.selectbox('County explanation', list(range(len(rows))),
                                format_func=lambda i: rows[i].get('County', rows[i].get('county', str(i))), key=key)
        row = rows[selected]
        for field, label in LABELS:
            st.markdown('**' + label + '**')
            st.write(row[field])
        st.caption(row['provenance'])
