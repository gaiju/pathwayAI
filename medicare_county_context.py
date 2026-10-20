"""Optional Original Medicare county context, separate from Lyme cost scenarios."""
from report_download import branded_download_button
import csv
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'
COUNTIES = {'36027': 'Dutchess', '36071': 'Orange'}
SOURCE_URL = 'https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-geographic-comparisons/medicare-geographic-variation-by-national-state-county'


def load_records():
    with (DATA / 'cms_medicare_dutchess_orange_2014_2024.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))


def county_records(records):
    """Never combine age strata, geographic levels, or duplicate county-year rows."""
    selected = [r for r in records if r['BENE_GEO_LVL'] == 'County'
                and r['BENE_AGE_LVL'] == 'All' and r['BENE_GEO_CD'] in COUNTIES]
    keys = [(r['BENE_GEO_CD'], int(r['YEAR'])) for r in selected]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate county-year records in the All age group')
    return selected


def common_years(records):
    selected = county_records(records)
    years = [{int(r['YEAR']) for r in selected if r['BENE_GEO_CD'] == fips}
             for fips in COUNTIES]
    return sorted(set.intersection(*years), reverse=True)


def _number(value):
    if value.strip() in ('', '*', '.', 'NA', 'N/A'):
        return None
    result = float(value.replace(',', ''))
    if not math.isfinite(result) or result < 0:
        raise ValueError('Invalid Medicare payment/count value')
    return result


def payment_rows(year=None, standardized=True, records=None):
    records = load_records() if records is None else records
    years = common_years(records)
    if not years or (year is not None and year not in years):
        raise ValueError('A matching year is required for both counties')
    year = years[0] if year is None else year
    selected = {r['BENE_GEO_CD']: r for r in county_records(records) if int(r['YEAR']) == year}
    prefix = 'STDZD_' if standardized else ''
    return [{'County': county, 'Year': year,
             'Original Medicare beneficiaries': _number(selected[fips]['BENES_OM_CNT']),
             'Inpatient': _number(selected[fips][f'IP_MDCR_{prefix}PYMT_PC']),
             'Hospital outpatient': _number(selected[fips][f'OP_MDCR_{prefix}PYMT_PC']),
             'Payment basis': 'Standardized' if standardized else 'Actual',
             'Unit': 'Annual USD per Original Medicare beneficiary',
             'Population': 'Original Medicare; All age group',
             'Geography': 'Beneficiary county of residence',
             'Source': SOURCE_URL}
            for fips, county in COUNTIES.items()]


def show_medicare_county_context():
    import pandas as pd
    import streamlit as st

    with st.expander('Medicare inpatient and hospital outpatient spending · county context'):
        st.write('Compare Medicare payments for people living in Dutchess and Orange. These figures cover Original Medicare, not everyone in the county.')
        st.caption('General healthcare context · not Lyme-specific costs or patient bills')
        try:
            records = load_records()
            years = common_years(records)
            if not years:
                raise ValueError('No matching years')
            year = st.selectbox('Year of care', years, key='cms_county_year')
            basis = st.radio('Payment comparison', ['Standardized', 'Actual'], horizontal=True, key='cms_county_payment_basis')
            rows = payment_rows(year, standardized=basis == 'Standardized', records=records)
        except (OSError, ValueError, KeyError) as error:
            st.warning('This Medicare comparison is unavailable. No estimates have been substituted.')
            return
        if basis == 'Standardized':
            st.write('Standardized payments adjust for geographic payment rates. They do not adjust for differences in health status.')
        else:
            st.write('Actual payments are reported Medicare program payments. They are not hospital charges or patients’ own payments.')
        st.write(f'{year} · annual dollars per Original Medicare beneficiary · all Original Medicare age groups')
        frame = pd.DataFrame(rows)
        st.dataframe(frame[['County', 'Original Medicare beneficiaries', 'Inpatient', 'Hospital outpatient']], hide_index=True,
                     column_config={'Original Medicare beneficiaries': st.column_config.NumberColumn(format='%d'),
                                    'Inpatient': st.column_config.NumberColumn(format='$%.2f'),
                                    'Hospital outpatient': st.column_config.NumberColumn(format='$%.2f')},
                     use_container_width=True)
        st.caption('Hospital outpatient means hospital outpatient department services. It does not include every service delivered outside a hospital. Per-beneficiary averages include people who did not use that service; they are not prices per visit or admission.')
        st.write('Use this to describe the healthcare spending context. These figures do not establish Lyme burden, service gaps, quality, or potential savings. Do not add them to the Lyme cost illustrations or personal cost record.')
        branded_download_button('Download this Medicare comparison', frame.to_csv(index=False).encode('utf-8-sig'),
                           file_name=f'PathwayAI_Medicare_County_Context_{year}_{basis}.csv', mime='text/csv', key='cms_county_download')
        st.markdown(f'[CMS dataset and documentation]({SOURCE_URL})')
        st.caption('Source: project-owner-supplied extract of the 2014–2024 CMS public use file. Column definitions checked against the supplied CMS dictionary; the full source CSV was not independently re-downloaded. Suppressed or missing values remain missing.')
