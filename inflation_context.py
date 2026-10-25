"""Optional general-purchasing-power restatement; no imputation or patient data."""
from decimal import Decimal
from pathlib import Path
import json


def inflation_metadata():
    data = json.loads((Path(__file__).parent / 'data/cpi_general_inflation.json').read_text())
    means = {}
    counts = {}
    for year in (2016, 2025):
        rows = [r for r in data['observations'] if r['date'].startswith(str(year))]
        vals = [Decimal(str(r['value'])) for r in rows if r['value'] is not None]
        if len(rows) != 12 or not vals:
            raise ValueError('Expected twelve monthly slots and at least one observed CPI value.')
        means[year] = sum(vals) / len(vals)
        counts[year] = len(vals)
    return {**{k:v for k,v in data.items() if k != 'observations'},
            'base_year':2016, 'target_year':2025, 'base_index':str(means[2016]),
            'target_index':str(means[2025]), 'factor':str(means[2025]/means[2016]),
            'base_months':counts[2016], 'target_months':counts[2025],
            'missing_months':[r['date'][:7] for r in data['observations'] if r['value'] is None],
            'method':'Arithmetic mean of available monthly index levels in each year; no missing values imputed.',
            'scope':'General purchasing-power comparison, not medical-care inflation, updated local costs or measured county spending.'}


def comparison_rows(county_only=False):
    factor = Decimal(inflation_metadata()['factor'])
    original = [('Localized disease · per case',1307),('Disseminated disease · per case',3251),('Overall study mean · per case',2032)]
    counties = [('Dutchess · 1,060 reported cases',1060*2032),('Orange · 964 reported cases',964*2032),('Both counties · 2,024 reported cases',2024*2032)]
    return [{'Measure':name,'Original · 2016 USD':amount,
             'Restated · 2025 USD (11 months)':float(Decimal(amount)*factor)}
            for name,amount in (([] if county_only else original)+counties)]


def inflation_text():
    meta=inflation_metadata()
    lines=['OPTIONAL GENERAL INFLATION COMPARISON',
           'Original study amounts remain in 2016 dollars. This comparison uses uploaded FRED monthly CPI-U data sourced from BLS.',
           '2016 average: '+meta['base_index']+' (12 months).',
           '2025 available-month average: '+meta['target_index']+' (11 months; October missing).',
           'Factor = 2025 available-month average / 2016 average = '+meta['factor'],
           meta['method'],
           'This is not presented as a verified official annual-average CPI value. No October value is invented.',
           meta['scope'],
           'Study figures: Hook et al. (2022). County cases: NYSDOH 2024, Dutchess 1,060; Orange 964. Full-precision factor applied before display rounding. Patient payments and other studies are unchanged.',
           'https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article',
           'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf',
           meta['source_url'],meta['bls_url'],'Source workbook SHA-256: '+meta['source_sha256']]
    for row in comparison_rows():
        lines.append(f"{row['Measure']}: original USD {row['Original · 2016 USD']:,}; restated USD {row['Restated · 2025 USD (11 months)']:,.2f}.")
    return '\n'.join(lines)


def export_rows(county_only=False):
    meta=inflation_metadata()
    return [{**row,**meta, 'cost_source':'https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article', 'county_case_year':2024, 'county_case_source':'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf'} for row in comparison_rows(county_only)]


def show_inflation_comparison(key,county_only=False):
    import streamlit as st
    from burden_framework import csv_bytes
    from report_download import branded_download_button
    with st.expander('Compare original costs with 2025 purchasing power'):
        mode=st.radio('Dollar view for this comparison', ['Original study dollars · 2016','2025 purchasing power · general inflation'],key=key+'_mode')
        adjusted=mode.startswith('2025')
        st.caption('This option changes only the comparison below; other charts retain their labeled study-year dollars.')
        rows=comparison_rows(county_only)
        if adjusted:
            st.info('Uses 11 available monthly CPI observations for 2025; October is missing. General inflation comparison, not a verified official annual-average restatement.')
            st.dataframe([{**r,'Original · 2016 USD':f"${r['Original · 2016 USD']:,.0f}", 'Restated · 2025 USD (11 months)':f"${r['Restated · 2025 USD (11 months)']:,.0f}"} for r in rows],hide_index=True,use_container_width=True)
        else:
            st.dataframe([{'Measure':r['Measure'],'Original · 2016 USD':f"${r['Original · 2016 USD']:,.0f}"} for r in rows],hide_index=True,use_container_width=True)
        st.caption('General price inflation changes purchasing power; it does not update treatment patterns, case mix or local prices. Study-based county illustrations remain separate from measured spending.')
        st.markdown('[FRED CPI-U data](https://fred.stlouisfed.org/series/CPIAUCNS) · [BLS series](https://data.bls.gov/timeseries/CUUR0000SA0)')
        st.download_button('Download original and restated amounts (CSV)',csv_bytes(export_rows(county_only)),file_name='PathwayAI_General_Inflation_Comparison.csv',mime='text/csv',key=key+'_csv')
        branded_download_button('Download inflation calculation and sources (PDF)',inflation_text().encode(),file_name='PathwayAI_Inflation_Methods.txt',mime='text/plain',key=key+'_pdf')
