"""A public-data county decision brief, independent of personal session records."""
from pathlib import Path
import json
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
from community_action_summary import (ACTION_AREAS, EVIDENCE_TYPES,
                                      audience_actions, healthcare_context, CDC_URL, HRSA_URL)
from community_action import ACTION_OPTIONS
from inflation_context import inflation_metadata
from county_planning_indicators import planning_indicators, planning_context_text, show_planning_indicators

BASE=Path(__file__).resolve().parent
REPORT_VERSION='1.4'
COUNTIES={'Dutchess':'36027','Orange':'36071'}


def build_report(county, priority, restate=False, audience='Public health departments'):
    if county not in COUNTIES or priority not in ACTION_OPTIONS:
        raise ValueError('Choose a supported county and planning priority.')
    cases=json.loads((BASE/'data/ny_lyme_cases_2024_verification.json').read_text())
    rates=json.loads((BASE/'data/ny_lyme_rates_2024_verification.json').read_text())
    hook=json.loads((BASE/'data/hook_2022_article_verification.json').read_text())
    count=cases['verified_lyme_case_counts'][county]
    unit=hook['societal_mean']
    total=count*unit
    access = healthcare_context(county)
    result={
        'prepared_date':datetime.now(ZoneInfo('America/New_York')).date().isoformat(),
        'audience':audience, 'audience_actions':audience_actions(audience),
        'community_action_areas':[dict(title=title, description=description) for title, description in ACTION_AREAS],
        'evidence_types':[dict(label=label, description=description) for label, description in EVIDENCE_TYPES if label != 'Patient survey findings'],
        'healthcare_context':access,
        'local_patient_reports_status':'No county-specific patient-reported findings are established in this brief.',
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
            {'purpose':'CDC surveillance interpretation; historical county file in app', 'period':'2019–2022 county file; separate from NYSDOH 2024', 'url':CDC_URL, 'status':'Background surveillance context, not an additional 2024 county estimate.'},
            {'purpose':'General healthcare resources', 'period':'2023 fields; AHRF 2024–2025 release', 'url':HRSA_URL, 'status':access['status']},
            {'purpose':'Societal study mean','period':'2016 dollars; recruitment 2014–2016','url':hook['source_url'],'status':hook['verification']},
        ],
        'privacy':'Public evidence and proposed planning actions only. No session stories, personal records or synthetic patient cards are included.',
        'scope':'Discussion brief, not a county demand assessment, benefits decision, funded service or adopted county plan.',
        'inflation':None,
    }
    result['additional_public_context'] = planning_indicators(county)
    for source in result['sources']:
        if source['url'] == HRSA_URL:
            source['purpose'] = 'Healthcare resources, insurance and poverty context'
            source['period'] = '2022 insurance fields; 2023 healthcare and poverty fields; AHRF 2024–2025 release'
    known_urls = {source['url'] for source in result['sources']}
    for source in result['additional_public_context']['sources']:
        if source['url'] not in known_urls:
            result['sources'].append({**source, 'status':'Existing source snapshot; no fresh retrieval.'})
            known_urls.add(source['url'])
    if restate:
        meta=inflation_metadata()
        result['inflation']={**meta,'restated_unit_usd':float(Decimal(unit)*Decimal(meta['factor'])),
                             'restated_total_usd':float(Decimal(total)*Decimal(meta['factor']))}
    return result


def report_text(report):
    from report_download import TAGLINE
    r=report
    access=r['healthcare_context']
    lines=[f"PathwayAI | {r['county']} County Lyme Burden & Action Report",
           TAGLINE, 'Public evidence and support planning · Version '+r['report_version'],
           'Prepared: '+r['prepared_date'],
           'Data years: Lyme surveillance 2024 · HRSA insurance 2022 · HRSA poverty and resources 2023',
           f"Original study-based cost illustration: USD {r['illustrative_total_2016_usd']:,.0f} in 2016 dollars.",
           *([f"Optional 2025 purchasing-power comparison: USD {r['inflation']['restated_total_usd']:,.0f} · 11 available months; general inflation."] if r['inflation'] else []),
           'Illustrations of scale, not measured county spending.',
           '', '1. OBSERVED PUBLIC HEALTH DATA',
           f"Reported Lyme cases: {r['reported_cases']:,} · {r['case_year']} · county FIPS {r['county_fips']}.",
           f"Reported rate: {r['reported_rate_per_100000']:g} per 100,000 residents. New York State: {r['state_reported_rate_per_100000']:g}.",
           'NYSDOH reports cases by residence, not all infections or where exposure occurred. CDC historical county files in the app cover 2019–2022; they are not combined with 2024 counts.',
           'Published rates are reproduced; exact population denominators and their vintage have not been independently verified.',
           '', 'Healthcare resource context · HRSA AHRF 2024–2025 release · 2023 fields']
    for label, value in access['indicators'].items():
        lines.append(label+': '+('Not available' if value is None else f'{value:,.0f}'))
    lines += [access['status'], access['limits'], '', planning_context_text(r['additional_public_context']),
              '', '2. STUDY-BASED COUNTY COST ILLUSTRATION',
              *([f"2025 purchasing-power illustration: {r['reported_cases']:,} reported cases × inflation-adjusted study mean ≈ USD {r['inflation']['restated_total_usd']:,.0f}.",
                 f"Inflation-adjusted study mean: approximately USD {r['inflation']['restated_unit_usd']:,.0f} per participant (rounded for display).",
                 'General inflation comparison using 11 available 2025 months; calculations use unrounded values. Original source calculation and study population are in Methods.']
                if r['inflation'] else [r['formula'], 'Hook et al. (published 2022): '+r['study_population']]),
              r['cost_perspective'],r['transfer_assumption'],r['other_assumptions'],
              'This illustrates scale, not today’s local costs. Hook excluded non-English speakers and nonacute disease; the study does not represent every local household.']
    if r['inflation']:
        m=r['inflation']
        lines += ['', 'Optional 2025 purchasing-power comparison · 11 available months',
                  f"2025 purchasing power: USD {m['restated_unit_usd']:,.0f} per participant; county illustration: USD {m['restated_total_usd']:,.0f}.",
                  f"General inflation only. 2016 mean CPI: {float(m['base_index']):.3f}; 2025 available-month mean: {float(m['target_index']):.3f}; factor approximately {float(m['factor']):.2f}.",
                  'Calculations use the full-precision factor retained in the methods CSV.',
                  '2025 has 11 observed months; October is missing. No imputation. This is not a verified official annual-average restatement.',
                  'Inflation changes purchasing power, not treatment patterns or local representativeness.',
                  m['source_url'],'Source workbook SHA-256: '+m['source_sha256']]
    lines += ['', '3. RESIDENT PRIORITIES TO DISCUSS',
              'Confirm priorities with residents and caregivers before choosing a response.',
              r['local_patient_reports_status'],
              '', 'What we still need to understand']+['- '+x for x in r['evidence_gaps']]
    lines += ['', '4. FROM LYME DISEASE BURDEN TO COMMUNITY ACTION',
              'Suggested actions for local review, not clinical advice or adopted programs.']
    for area in r['community_action_areas']:
        lines.append(area['title']+': '+area['description'])
    lines += ['', 'Planning audience: '+r['audience']]+['- '+item for item in r['audience_actions']]
    plan=r['planning']
    lines += ['', '5. A SUPPORT QUESTION TO DISCUSS',r['priority'],
              'Planning question: '+plan['decision'],'Possible response: '+plan['action'],
              'Who could help: '+plan['participants'],
              'These are proposed discussion topics, not findings about local demand or commitments from partners.',
              '', '6. WHAT TO CHECK BEFORE STARTING A PILOT']+['- '+x for x in r['feasibility_checks']]
    lines += ['', '7. CHECK WHETHER PEOPLE RECEIVED SUPPORT',
              'Choose a common follow-up period, such as 30 days. Record the starting situation and support received. Keep unanswered questions marked as unknown.',
              'For this priority, check: '+plan['measure'],
              'Use findings to improve support. Before/after changes alone do not establish that the tool caused improvements or saved money.',
              '', '8. DATA SOURCES AND METHODS',
              'Source status: Existing source snapshots. Newer official releases have not been verified for this brief.']
    if r['inflation']:
        lines += ['', 'Original study basis (retained for traceability)',r['formula'],
                  'Hook et al. (published 2022): '+r['study_population']]
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


def show_county_report(audience='Public health departments'):
    import streamlit as st
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
    report=build_report(county,priority,restate,audience=audience)
    with st.container(border=True):
        st.markdown('**'+county+' County · Report preview**')
        st.write(f"Reported: {report['reported_cases']:,} cases in 2024 · {report['reported_rate_per_100000']:g} per 100,000 residents.")
        st.write(f"Study-based illustration: USD {report['illustrative_total_2016_usd']:,.0f} · 2016 dollars.")
        st.write('Planning question: '+report['planning']['decision'])
        st.write('Audience: '+report['audience'])
        st.caption('Also included: county comparisons, HRSA indicators, language context and suggested community actions.')
        st.caption('Public-data report; proposed actions require local review. Personal entries are kept separate.')
    show_planning_indicators(report['additional_public_context'])
    from county_brief_pdf import county_brief_pdf
    st.download_button('Download county burden & action report (PDF)',
                       county_brief_pdf(report),
                       file_name=f'PathwayAI_{county}_County_Burden_Action_Report.pdf',mime='application/pdf',key='county_report_pdf',type='primary')
    with st.expander('Inspect calculations, sources and report data'):
        st.text(report['formula'])
        st.write(report['transfer_assumption'])
        for source in report['sources']:
            st.markdown('['+source['purpose']+']('+source['url']+') · '+source['period'])
        st.download_button('Download report data and methods (CSV)',csv_bytes(report_csv_rows(report)),file_name=f'PathwayAI_{county}_County_Burden_Action_Report.csv',mime='text/csv',key='county_report_csv')
    st.caption('After downloading: confirm local services, contacts, staffing, costs and responsibilities with residents and potential partners.')
