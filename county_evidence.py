"""Source-backed Hudson Valley demonstration values; never patient session data."""
import json
import math
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
COUNTY_FIPS = {'Dutchess': '36027', 'Orange': '36071'}
LANGUAGE_HOME = {'Dutchess': 16.2, 'Orange': 30.2}
HRSA_URL = 'https://data.hrsa.gov/topics/health-workforce/nchwa/ahrf'


def county_surveillance():
    cases = json.loads((BASE / 'data/ny_lyme_cases_2024_verification.json').read_text())
    rates = json.loads((BASE / 'data/ny_lyme_rates_2024_verification.json').read_text())
    return [dict(county=county, fips=fips, case_year=2024,
                 reported_cases=cases['verified_lyme_case_counts'][county],
                 reported_rate=rates['verified_rates'][county],
                 rate_unit='reported cases per 100,000 residents',
                 case_source=cases['source_url'], rate_source=rates['source_url'],
                 evidence_type='official reported surveillance',
                 verification='Previously checked supplied official PDFs, page 5; no fresh source retrieval.',
                 denominator_status='Official published rate; exact population denominator and vintage not independently verified.')
            for county, fips in COUNTY_FIPS.items()]


def state_surveillance():
    cases = json.loads((BASE / 'data/ny_lyme_cases_2024_verification.json').read_text())
    rates = json.loads((BASE / 'data/ny_lyme_rates_2024_verification.json').read_text())
    return dict(county='New York State', reported_cases=cases['verified_lyme_case_counts']['New York State'],
                reported_rate=rates['verified_rates']['NYS TOTAL'],case_year=2024,
                case_source=cases['source_url'],rate_source=rates['source_url'])


def _number(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


@lru_cache(maxsize=1)
def healthcare_capacity():
    """Read selected public 2023 fields from existing AHRF asset, with explicit missingness."""
    import pandas as pd
    import zipfile
    fields = {'pcp': 'phys_nf_prim_care_pc_exc_rsdt_23', 'hosp': 'hosp_23', 'beds': 'hosp_beds_23'}
    path = BASE / 'AHRF_2024-2025_CSV.zip'
    empty = {county: {**{key: None for key in fields}, 'year': 2023, 'source_url': HRSA_URL,
                       'status': 'Source unavailable; no values substituted.'} for county in COUNTY_FIPS}
    if not path.exists():
        return empty
    try:
        with zipfile.ZipFile(path) as archive:
            name = next(n for n in archive.namelist() if n.endswith('AHRF2025.csv'))
            frame = pd.read_csv(archive.open(name), usecols=['fips_st_cnty', *fields.values()], dtype={'fips_st_cnty': str})
        for county, fips in COUNTY_FIPS.items():
            selected = frame[frame['fips_st_cnty'].str.zfill(5) == fips]
            if len(selected) == 1:
                empty[county] = {**{key: _number(selected.iloc[0][field]) for key, field in fields.items()},
                                 'year': 2023, 'source_url': HRSA_URL,
                                 'status': 'Existing HRSA AHRF 2024–2025 asset; 2023 general resource counts, not appointments or Lyme expertise.'}
        return empty
    except (OSError, ValueError, KeyError, StopIteration, zipfile.BadZipFile):
        return empty


def language_context(county):
    if county not in COUNTY_FIPS:
        raise ValueError('Unsupported demonstration county')
    return {'county': county, 'percent': LANGUAGE_HOME[county], 'period': 'ACS 2020–2024',
            'population': 'Residents age 5 and older', 'measure': 'Language other than English spoken at home',
            'source_url': 'https://www.census.gov/quickfacts/' + county.lower() + 'countynewyork',
            'status': 'Previously supplied QuickFacts context; not a measure of English proficiency or interpreter demand.'}


def show_regional_overview():
    import streamlit as st
    st.markdown('### A Hudson Valley starting point')
    st.write('Explore Lyme disease patterns, study-based economic burden and support questions, starting with Dutchess and Orange counties. Other Hudson Valley counties are not yet included in this demonstration.')
    for col, row in zip(st.columns(2), county_surveillance()):
        with col, st.container(border=True):
            st.markdown('#### ' + row['county'] + ' County')
            st.metric('Reported Lyme cases · 2024', f"{row['reported_cases']:,}")
            st.write(f"{row['reported_rate']:g} reported cases per 100,000 residents")
    st.caption('NYSDOH 2024 surveillance · county of residence. These are reported cases, not all infections or exposure locations.')
    st.markdown('#### From local evidence to a useful discussion')
    st.markdown('1. **Explore:** start with the two-county picture above.\n2. **Compare:** choose Lyme, language or other context in Compare.\n3. **Understand burden:** review published economics and clearly labeled patient-reported evidence in Burden.\n4. **Choose a question:** identify one support priority in Plan.\n5. **Download:** take a sourced county brief to a team or partner discussion.')
    st.markdown('#### What the evidence can help you ask')
    st.write('Would prevention education, affordable-care navigation, language assistance or transport support be useful locally? Confirm needs and service capacity with residents before proposing a response.')
    st.caption('Demonstration using public data. County or organizational participation and endorsement are not implied. Personal records remain separate; shared reporting would require a governed, consent-based pilot.')
    with st.expander('Data behind this regional view'):
        for row in county_surveillance():
            st.markdown('[' + row['county'] + ' cases](' + row['case_source'] + ') · [Reported rates](' + row['rate_source'] + ')')
        st.write(county_surveillance()[0]['denominator_status'])
        st.write('Rates are taken from the official source; PathwayAI does not reconstruct them using a different population year.')
