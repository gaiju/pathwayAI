"""A public-data county decision brief, independent of personal session records."""
from pathlib import Path
import json
from decimal import Decimal
from community_action import ACTION_OPTIONS
from inflation_context import inflation_metadata

BASE=Path(__file__).resolve().parent
REPORT_VERSION='1.0'
COUNTIES={'Dutchess':'36027','Orange':'36071'}


def build_report(county, priority, restate=False):
    if county not in COUNTIES or priority not in ACTION_OPTIONS:
        raise ValueError('Choose a supported county and planning priority.')
    cases=json.loads((BASE/'data/ny_lyme_cases_2024_verification.json').read_text())
    rates=json.loads((BASE/'data/ny_lyme_rates_2024_verification.json').read_text())
    hook=json.loads((BASE/'data/hook_2022_article_verification.json').read_text())
    count=cases['verified_lyme_case_counts'][county]
    unit=hook['societal_mean']
    total=count*unit
    result={
        'report_version':REPORT_VERSION,'county':county,'state':'New York','county_fips':COUNTIES[county],
        'reported_cases':count,'case_year':2024,'reported_rate_per_100000':rates['verified_rates'][county],
        'state_reported_rate_per_100000':rates['verified_rates']['NYS TOTAL'],
        'study_societal_mean_usd':unit,'study_dollar_year':2016,'illustrative_total_2016_usd':total,
        'study_population':'613 participants in societal analysis; reported cases recruited in four high-incidence states during 2014–2016.',
        'cost_perspective':'Societal: medical, nonmedical and productivity costs; components are already included.',
        'formula':f'{count:,} reported cases × USD {unit:,} study mean = USD {total:,} (2016 dollars).',
        'transfer_assumption':'Applying this study mean to reported county cases is an assumption; the result is not measured local spending.',
        'other_assumptions':'No adjustment for underreporting or local case mix. No causal savings or disability probabilities are inferred.',
        'priority':priority,'planning':dict(ACTION_OPTIONS[priority]),
        'evidence_gaps':['Lyme-attributable county disability and duration','Continuing costs beyond the study follow-up','Local unmet care and support needs','Experiences of people excluded or underrepresented in the source study'],
        'feasibility_checks':['Confirm local demand with residents and caregivers, including assisted/offline participation.','Verify current services, eligibility, interpreter access and appointment capacity.','Agree who is responsible and estimate staff time, program costs and a funding source.','Define consent, minimal data collection, access, retention and deletion before any collection.'],
        'evaluation':'Agree a common reporting period and baseline, record missing answers, measure support received and unresolved needs. Before/after changes alone do not establish causality or savings.',
        'sources':[
            {'purpose':'Reported cases, county of residence','period':'2024','url':cases['source_url'],'status':'Previously checked supplied official PDF, page 5.'},
            {'purpose':'Reported rates per 100,000','period':'2024','url':rates['source_url'],'status':'Previously checked supplied official PDF, page 5.'},
            {'purpose':'Societal study mean','period':'2016 dollars; recruitment 2014–2016','url':hook['source_url'],'status':hook['verification']},
        ],
        'privacy':'Public evidence and proposed planning actions only. No session stories, personal records or synthetic patient cards are included.',
        'scope':'Discussion brief, not a county demand assessment, benefits decision, funded service or adopted county plan.',
        'inflation':None,
    }
    if restate:
        meta=inflation_metadata()
        result['inflation']={**meta,'restated_unit_usd':float(Decimal(unit)*Decimal(meta['factor'])),
                             'restated_total_usd':float(Decimal(total)*Decimal(meta['factor']))}
    return result


def report_text(report):
    from report_download import TAGLINE
    r=report
    lines=[f"PathwayAI | {r['county']} County Lyme Burden & Action Report",
           TAGLINE, 'New York · Public evidence and support planning · Report version '+r['report_version'],
           '', '1. OBSERVED PUBLIC EVIDENCE',
           f"Reported Lyme cases: {r['reported_cases']:,} · {r['case_year']} · county FIPS {r['county_fips']}.",
           f"Reported rate: {r['reported_rate_per_100000']:g} per 100,000 residents. New York State: {r['state_reported_rate_per_100000']:g}.",
           'Surveillance describes reported cases by residence, not all infections or where exposure occurred.',
           '', '2. STUDY-BASED ECONOMIC ILLUSTRATION',r['formula'],r['study_population'],r['cost_perspective'],r['transfer_assumption'],r['other_assumptions'],
           'Hook excluded non-English speakers and nonacute disease; the study does not represent every local household.']
    if r['inflation']:
        m=r['inflation']
        lines += ['', 'OPTIONAL 2025 PURCHASING-POWER COMPARISON',
                  f"Per case: USD {m['restated_unit_usd']:,.0f}; county illustration: USD {m['restated_total_usd']:,.0f}.",
                  'General inflation only. 2016 mean CPI: '+m['base_index']+'; 2025 available-month mean: '+m['target_index']+'; factor: '+m['factor'],
                  '2025 has 11 observed months; October is missing. No imputation. This is not a verified official annual-average restatement.',
                  m['source_url'],'Source workbook SHA-256: '+m['source_sha256']]
    lines += ['', '3. ADDITIONAL BURDEN TO MEASURE']+['- '+x for x in r['evidence_gaps']]
    plan=r['planning']
    lines += ['', '4. SUPPORT DECISION TO EXPLORE',r['priority'],
              'Planning question: '+plan['decision'],'Possible response: '+plan['action'],
              'Potential partners to approach: '+plan['participants'],
              'These are proposed discussion topics, not findings about local demand or commitments from partners.',
              '', '5. CHECK FEASIBILITY BEFORE A PILOT']+['- '+x for x in r['feasibility_checks']]
    lines += ['', '6. AGREE ON FOLLOW-UP','Candidate measures: '+plan['measure'],r['evaluation'],
              '', 'SOURCES AND METHODS']
    for source in r['sources']:
        lines += [source['purpose']+' · '+source['period'],source['url'],source['status']]
    lines += ['',r['privacy'],r['scope']]
    return '\n'.join(lines)


def report_csv_rows(report):
    from copy import deepcopy
    row=deepcopy(report)
    for key,value in list(row.items()):
        if isinstance(value,(dict,list)):
            row[key]=json.dumps(value,ensure_ascii=False,sort_keys=True)
    return [row]


def show_county_report():
    import streamlit as st
    from report_download import branded_download_button
    from burden_framework import csv_bytes
    st.markdown('### Download a county burden & action report')
    st.write('Take a sourced report to a team discussion: reported cases, study-based costs, evidence gaps and one support decision to explore.')
    a,b=st.columns(2)
    with a:
        county=st.selectbox('County for the report',list(COUNTIES),key='county_report_county')
    with b:
        priority=st.selectbox('Support priority to explore',list(ACTION_OPTIONS),key='county_report_priority')
    restate=st.checkbox('Include the optional 2025 purchasing-power comparison',value=False,key='county_report_inflation')
    if restate:
        st.caption('General inflation using 11 available months in 2025; October missing. Original 2016-dollar amounts remain in the report.')
    report=build_report(county,priority,restate)
    with st.container(border=True):
        st.markdown('**'+county+' County · Report preview**')
        st.write(f"Reported: {report['reported_cases']:,} cases in 2024 · {report['reported_rate_per_100000']:g} per 100,000 residents.")
        st.write(f"Study-based illustration: USD {report['illustrative_total_2016_usd']:,.0f} · 2016 dollars.")
        st.write('Planning question: '+report['planning']['decision'])
        st.caption('Public-data report; proposed actions require local review. Personal entries are kept separate.')
    branded_download_button('Download county burden & action report (PDF)',report_text(report).encode(),file_name=f'PathwayAI_{county}_County_Burden_Action_Report.txt',mime='text/plain',key='county_report_pdf',type='primary')
    with st.expander('Inspect calculations, sources and report data'):
        st.text(report['formula'])
        st.write(report['transfer_assumption'])
        for source in report['sources']:
            st.markdown('['+source['purpose']+']('+source['url']+') · '+source['period'])
        st.download_button('Download report data and methods (CSV)',csv_bytes(report_csv_rows(report)),file_name=f'PathwayAI_{county}_County_Burden_Action_Report.csv',mime='text/csv',key='county_report_csv')
    st.caption('After downloading: confirm local services, contacts, staffing, costs and responsibilities with residents and potential partners.')
