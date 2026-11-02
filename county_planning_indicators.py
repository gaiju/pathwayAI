"""Additional public context for the two-county pilot; no patient aggregation."""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
COUNTIES = {'Dutchess': '36027', 'Orange': '36071'}
LANGUAGE_HOME = {'Dutchess': 16.2, 'Orange': 30.2}
CASE_URL = 'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf'
RATE_URL = 'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf'
TREND_URL = 'https://www.dutchessny.gov/Departments/DBCH/Docs/MHRCHA2025.pdf'


def _read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def planning_indicators(county, base=None):
    if county not in COUNTIES:
        raise ValueError('Choose a supported county.')
    root = Path(base) if base is not None else BASE
    cases = _read_json(root / 'data/ny_lyme_cases_2024_verification.json')
    rates = _read_json(root / 'data/ny_lyme_rates_2024_verification.json')
    regional = _read_json(root / 'data/mid_hudson_lyme_rates_verification.json')
    comparison = []
    for area in [*COUNTIES, 'New York State']:
        comparison.append({'Area': area, 'Year': 2024,
                           'Reported cases': cases.get('verified_lyme_case_counts', {}).get(area),
                           'Reported cases per 100,000': rates.get('verified_rates', {}).get('NYS TOTAL' if area == 'New York State' else area)})
    trend = [{'Year': year, 'Reported cases per 100,000': regional.get('rates', {}).get(str(year), {}).get(county)}
             for year in (2022, 2023)]
    trend.append({'Year': 2024, 'Reported cases per 100,000': rates.get('verified_rates', {}).get(county)})
    initiatives = []
    try:
        with (root / 'pathwayai_county_assets.csv').open(newline='') as source:
            for row in csv.DictReader(source):
                if row.get('fips') == COUNTIES[county] and row.get('url', '').startswith('https://'):
                    initiatives.append({key: row.get(key, '') for key in ('name', 'owner', 'url', 'category')})
    except OSError:
        pass
    census_url = 'https://www.census.gov/quickfacts/' + county.lower() + 'countynewyork'
    return {
        'county': county, 'comparison': comparison, 'rate_trend': trend,
        'language_context': {'value': LANGUAGE_HOME[county], 'unit': 'percent',
                             'measure': 'Language other than English spoken at home',
                             'population': 'Residents age 5 and older', 'period': 'ACS 2020–2024',
                             'source_url': census_url,
                             'status': 'Existing app QuickFacts snapshot; not freshly retrieved.',
                             'limits': 'Not a measure of English proficiency, immigration status or interpreter demand.'},
        'listed_initiatives': initiatives,
        'initiative_status': 'Existing public directory snapshot; current contacts, activity, eligibility and availability must be verified. No listing does not mean no services exist.',
        'planning_questions': [
            'How do the reported rate and case count compare with the neighboring county and state?',
            'Which prevention and outreach questions should residents and partners explore in light of the reported-rate trend?',
            'Which languages and communication formats do residents actually prefer?',
            'Could existing county initiatives help, and what staffing, service capacity or support gaps need checking?'],
        'limits': 'Reported disease by residence, not exposure location or all infections. Trend years use different source publications; do not infer causes, changes in access or savings. Pre-2022 rates are excluded because surveillance definitions changed. Published 2024 rates are reproduced without reconstructing population denominators.',
        'sources': [
            {'purpose': 'County/state reported cases', 'period': '2024', 'url': CASE_URL},
            {'purpose': 'County/state reported rates', 'period': '2024', 'url': RATE_URL},
            {'purpose': 'Reported rate trend, Figure 147, page 219', 'period': '2022–2023; regional assessment published 2025', 'url': regional.get('source_url', TREND_URL)},
            {'purpose': 'Language spoken at home, age 5+', 'period': 'ACS 2020–2024', 'url': census_url}],
    }


def _display(value, suffix=''):
    if value is None:
        return 'Not available'
    return f'{value:,g}'+suffix


def planning_context_text(context):
    lines = ['COUNTY COMPARISONS AND PLANNING CONTEXT', 'Reported surveillance · 2024']
    for row in context['comparison']:
        lines.append(row['Area']+': '+_display(row['Reported cases'])+' reported cases; '+_display(row['Reported cases per 100,000'])+' per 100,000 residents.')
    lines += ['', context['county']+' reported-rate trend · cases per 100,000']
    lines += [str(row['Year'])+': '+_display(row['Reported cases per 100,000']) for row in context['rate_trend']]
    language = context['language_context']
    lines += [context['limits'], '', language['measure']+': '+_display(language['value'], '%'),
              language['population']+' · '+language['period'], language['status'], language['limits'],
              '', 'Existing county initiatives to check']
    if not context['listed_initiatives']:
        lines.append('Not available in this directory snapshot; verify with local partners.')
    for item in context['listed_initiatives']:
        lines += [item['name']+' · '+item['owner']+' · '+item['category'], item['url']]
    lines += [context['initiative_status'], '', 'Questions these indicators can help you ask']
    lines += ['- '+q for q in context['planning_questions']]
    return '\n'.join(lines)


def show_planning_indicators(context):
    import streamlit as st
    with st.expander('More county planning data: comparisons, trends, language and local initiatives'):
        st.markdown('**County and state comparison · 2024 reported surveillance**')
        rows = [{key: (_display(value) if key not in ('Area', 'Year') else value) for key, value in row.items()}
                for row in context['comparison']]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.markdown('**'+context['county']+' reported-rate trend**')
        st.dataframe([{'Year': row['Year'], 'Reported cases per 100,000': _display(row['Reported cases per 100,000'])}
                      for row in context['rate_trend']], hide_index=True, use_container_width=True)
        st.caption(context['limits'])
        language = context['language_context']
        st.write('**Language context:** '+_display(language['value'], '%')+' speak a language other than English at home · age 5+ · '+language['period']+'.')
        st.caption(language['status']+' '+language['limits'])
        st.markdown('**Existing county initiatives to check**')
        if not context['listed_initiatives']:
            st.write('No listings in this directory snapshot. Ask local partners what is available.')
        for item in context['listed_initiatives']:
            st.markdown('['+item['name']+']('+item['url']+') · '+item['owner'])
        st.caption(context['initiative_status'])
        st.markdown('**Questions to discuss with residents and partners**')
        for question in context['planning_questions']:
            st.markdown('- '+question)
        st.caption('These indicators are included in the PDF and methods CSV. No individual needs, county demand, disability counts or savings are inferred.')
