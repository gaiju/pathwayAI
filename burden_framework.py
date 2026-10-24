"""Versioned public-evidence framework; independent of patient session records."""
from pathlib import Path
import csv
import io
import json

BASE = Path(__file__).resolve().parent
VERSION = '0.1.0'
REVIEW_DATE = '2026-10-23'
SNAPSHOT = 'https://github.com/gaiju/pathwayAI/tree/burden-evidence-v0.1.0'
CITATION = ('Zhang, Y. (2026). PathwayAI: Lyme disease burden evidence framework '
            '(Version 0.1.0) [Software and methods]. ' + SNAPSHOT)
SOURCES = [
    {'id': 'hook2022', 'citation': 'Hook SA et al. (2022). Economic Burden of Reported Lyme Disease in High-Incidence Areas, United States, 2014–2016. Emerging Infectious Diseases, 28(6).',
     'url': 'https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article', 'status': 'Previously reviewed supplied article text; linked tables not separately retrieved.'},
    {'id': 'adrion2015', 'citation': 'Adrion ER, Aucott J, Lemke KW, Weiner JP. (2015). Health Care Costs, Utilization and Patterns of Care following Lyme Disease. PLOS ONE, 10(2):e0116767.',
     'url': 'https://doi.org/10.1371/journal.pone.0116767', 'status': 'Uploaded full PDF reviewed.'},
    {'id': 'johnson2014', 'citation': 'Johnson L, Wilcox S, Mankoff J, Stricker RB. (2014). Severity of chronic Lyme disease compared to other chronic conditions: a quality of life survey. PeerJ, 2:e322.',
     'url': 'https://doi.org/10.7717/peerj.322', 'status': 'Uploaded full PDF reviewed; table/narrative discrepancies recorded.'},
    {'id': 'horn2025', 'citation': 'Horn EJ et al. (2025). Lyme Disease Biobank: 10 years of 3 month follow-up visits from 2014 to 2023. Frontiers in Medicine, 12:1577936.',
     'url': 'https://doi.org/10.3389/fmed.2025.1577936', 'status': 'Uploaded full PDF reviewed.'},
    {'id': 'panel2016', 'citation': 'Sanders GD et al. (2016). Recommendations for Conduct, Methodological Practices, and Reporting of Cost-effectiveness Analyses: Second Panel on Cost-Effectiveness in Health and Medicine. JAMA, 316(10):1093–1103.',
     'url': 'https://doi.org/10.1001/jama.2016.12195', 'status': 'Bibliographic reference and supplied summary; full article not retrieved. Framework is adapted, not a claim of complete Panel compliance.'},
]


def evidence_rows():
    hook = json.loads((BASE / 'data/hook_2022_article_verification.json').read_text())
    adrion = json.loads((BASE / 'data/adrion_2015_uploaded_pdf_review.json').read_text())
    national = hook['national_illustrations_usd']
    common = {'framework_version': VERSION, 'review_date': REVIEW_DATE}
    rows = [
        {'measure': 'Published national societal-cost illustration: lower endpoint', 'value': national['median_based'], 'unit': 'USD', 'geography': 'United States', 'perspective': 'Societal', 'period': 'Annual national illustration published in Hook 2022', 'dollar_year': hook['dollar_year'], 'source_id': 'hook2022', 'interpretation': 'Author-reported historical illustration; not a current national measurement, lifetime total or confidence limit.'},
        {'measure': 'Published national societal-cost illustration: upper endpoint', 'value': national['mean_based'], 'unit': 'USD', 'geography': 'United States', 'perspective': 'Societal', 'period': 'Annual national illustration published in Hook 2022', 'dollar_year': hook['dollar_year'], 'source_id': 'hook2022', 'interpretation': 'Author-reported historical illustration; not added to lower endpoint. Original national arithmetic is not recomputed here.'},
        {'measure': 'Societal cost per study participant', 'value': hook['societal_mean'], 'unit': 'USD per participant', 'geography': 'Four high-incidence U.S. states', 'perspective': 'Societal', 'period': 'Study follow-up; recruitment 2014–2016', 'dollar_year': hook['dollar_year'], 'source_id': 'hook2022', 'interpretation': 'Includes medical, nonmedical and productivity components; not a lifetime total.'},
    ]
    for row in adrion['findings']:
        rows.append({'measure': row['measure'], 'value': row['usd'], 'unit': 'USD adjusted difference per person', 'geography': 'U.S. commercial-insurance study', 'perspective': 'Medical insurer-allowed amounts', 'period': '12-month outcome; claims 2006–2010', 'dollar_year': 'Not established from reviewed text', 'source_id': 'adrion2015', 'interpretation': 'Historical association; comparison groups differ. Do not sum with other references or use as current patient bills.'})
    for row in rows:
        row.update(common)
        row['source_url'] = next(s['url'] for s in SOURCES if s['id'] == row['source_id'])
    return rows


def impact_inventory():
    return [
        {'Component': 'Medical care', 'Available evidence': 'Hook societal medical component; Adrion claims-based costs; entered patient payments', 'Coverage / next evidence needed': 'Different perspectives and horizons; current Lyme-specific county spending remains unmeasured.'},
        {'Component': 'Travel and other household spending', 'Available evidence': 'Optional personal cost records; part of Hook nonmedical costs', 'Coverage / next evidence needed': 'Comparable local records and reporting periods; no representative county average.'},
        {'Component': 'Work disruption', 'Available evidence': 'Missed workdays; optional valuation; Johnson selected survey', 'Coverage / next evidence needed': 'Reduced hours, stopped work, reduced effectiveness and duration; prevent overlapping loss estimates.'},
        {'Component': 'Unpaid caregiving', 'Available evidence': 'Optional hours entered in personal records', 'Coverage / next evidence needed': 'Agreed time period and valuation method; no current county dollar estimate.'},
        {'Component': 'Daily function and quality of life', 'Available evidence': 'Patient descriptions; Johnson survey; Horn follow-up', 'Coverage / next evidence needed': 'Repeated, standardized measures; symptoms, limitations and benefits receipt are different outcomes.'},
        {'Component': 'Longer-term disability and continuing costs', 'Available evidence': 'Selected illness studies; separate HRSA/Census all-cause context', 'Coverage / next evidence needed': 'Appropriate probability, duration, affected population and incremental cost. Not estimated from three-month symptoms or selected-survey percentages.'},
    ]


def csv_bytes(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8-sig')


def evidence_package():
    return {'title': 'PathwayAI Lyme disease burden evidence framework', 'version': VERSION,
            'review_date': REVIEW_DATE, 'citation': CITATION,
            'measures': evidence_rows(), 'impact_inventory': impact_inventory(), 'sources': SOURCES,
            'scope': {'current_national_estimate': False, 'global_cost_total': None,
                      'county_lyme_disability_estimate': None,
                      'patient_entries_included': False,
                      'note': 'Published evidence and planning illustrations; no live national feed, new population estimate, proven savings or cost-effectiveness analysis.'}}


def methods_text():
    lines = ['PathwayAI | U.S. Lyme burden evidence and methods', 'Version: ' + VERSION,
             'Evidence review: ' + REVIEW_DATE, '', 'PURPOSE',
             'Connect county surveillance with published U.S. economic and functional evidence. Document measured, assumed and missing components.',
             '', 'NATIONAL CONTEXT',
             'Hook reports annual national societal-cost illustrations of $345 million to $968 million in 2016 dollars. These historical reference points are not current spending or statistical confidence limits. The original national calculation is not recomputed here.',
             '', 'THREE DISTINCT QUESTIONS',
             'Annual new-case burden: costs attached to a defined group of newly occurring cases over a specified follow-up period.',
             'Ongoing population burden: costs and functional effects among people still affected, including earlier years of onset.',
             'Lifetime burden: cumulative effects over a longer horizon; not estimated by this framework.',
             '', 'COST PERSPECTIVES AND DOUBLE COUNTING',
             'Household payments, insurer-allowed medical spending and societal totals answer different questions. Hook societal totals already include medical, nonmedical and productivity components. Do not add the Adrion differences, patient payments or another work-loss estimate to them.',
             'Adrion reports different adjusted comparisons over 12 months, not causal savings or lifetime cost. Claims cover commercially insured ages 0–64 in 2006–2010; a single common dollar year was not established in the reviewed text.',
             '', 'COUNTY CALCULATION',
             'Reported cases × $2,032 Hook societal mean = a transfer-based illustration in 2016 dollars. Applying the study experience to a county is an assumption, not a direct county measurement.',
             'Dutchess: 1,060 reported cases × $2,032 = $2,153,920. Orange: 964 × $2,032 = $1,958,848. Reported case year: 2024.',
             'Case source: https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf',
             '', 'FUNCTION AND DISABILITY',
             'Johnson describes selected persistent-illness respondents. Horn describes selected early-care follow-up participants. Neither supplies a directly transportable probability of county Lyme disability. All-cause HRSA/Census disability stays separate.',
             '', 'INTERNATIONAL COMPARISON',
             'Country comparisons need compatible case definitions, reporting coverage, time horizons, local unit costs and currency/price years. No global total is calculated. U.S. unit costs are not applied worldwide.',
             'International surveillance discovery: https://www.ecdc.europa.eu/en/borreliosis (portal not freshly reviewed; not a numerical input).',
             '', 'BURDEN INVENTORY']
    for row in impact_inventory():
        lines.append(' | '.join(f'{k}: {v}' for k, v in row.items()))
    lines += ['', 'UNCERTAINTY AND EVIDENCE STATUS',
              'Scenario ranges require documented assumptions. Statistical uncertainty needs an appropriate model; arbitrary ranges are not confidence intervals. Current references do not establish PathwayAI savings, resource-allocation effects or disability reduction.',
              'Sources use different populations, periods and price years. New web downloads were blocked. Paper verification is based on supplied documents; original studies, not PathwayAI, generated the cited findings.',
              'Hook excluded non-English speakers and nonacute disease. The evidence inventory therefore highlights important gaps for the communities PathwayAI aims to serve.',
              '', 'REFERENCES']
    for source in SOURCES:
        lines += [source['citation'], source['url'], 'Review status: ' + source['status'], '']
    lines += ['CITE THIS FRAMEWORK', CITATION,
              'Cite the original study for its findings. This citation identifies software/methods, not a peer-reviewed study, government estimate, endorsement or DOI-registered archive.']
    return '\n'.join(lines)


def show_us_burden(simple=True):
    import streamlit as st
    from report_download import branded_download_button

    st.markdown('### U.S. Lyme disease burden')
    st.write('Connect the national picture with county planning: what illness costs, who bears those costs, and which effects remain unmeasured.')
    hook = json.loads((BASE / 'data/hook_2022_article_verification.json').read_text())
    national = hook['national_illustrations_usd']
    with st.container(border=True):
        st.markdown('**Published national economic benchmark**')
        st.metric('Annual societal-cost illustrations · Hook et al. (2022)',
                  f"${national['median_based']/1e6:,.0f}–{national['mean_based']/1e6:,.0f} million")
        st.write('2016 U.S. dollars · Historical published illustrations, not current national spending or a confidence interval.')
        st.markdown('[Read the original study](' + SOURCES[0]['url'] + ')')
    st.markdown('**Read the burden at three levels**\n\n- **New illness:** reported cases and study-based episode costs.\n- **Ongoing effects:** continuing symptoms, work disruption and unpaid care, including illness from earlier years.\n- **Community needs:** access to care and support, informed by local evidence and future consented contributions.')
    branded_download_button('Download U.S. burden evidence and methods', methods_text().encode('utf-8'),
                            file_name='PathwayAI_US_Burden_Methods.txt', mime='text/plain', key='us_burden_methods', type='primary')
    with st.expander('What the burden includes', expanded=not simple):
        st.dataframe(impact_inventory(), hide_index=True, use_container_width=True)
        st.write('Keep societal totals, household payments and medical-spending studies separate. Existing totals already include some of the components above.')
    with st.expander('Medical spending and lasting functional effects'):
        st.write('Adrion et al. (2015): Lyme cases were associated with 2,968 dollars in higher adjusted medical costs than matched controls over 12 months. In a separate within-Lyme comparison, symptom-related diagnoses were associated with 3,798 dollars in higher costs. These are separate historical allowed-amount comparisons, not amounts to add.')
        st.write('Johnson et al. (2014) describes work and functional impacts in a selected persistent-illness survey. Horn et al. (2025) supports follow-up questions. Neither establishes a county long-term disability rate.')
        for source in SOURCES[1:4]:
            st.markdown('[' + source['citation'] + '](' + source['url'] + ')')
    with st.expander('International comparisons'):
        st.write('A useful international comparison preserves each country’s case definition, reporting coverage, local costs and price year. U.S. prices cannot simply be multiplied by worldwide cases.')
        st.write('This version presents U.S. evidence and a framework for country-specific comparisons. A global economic total requires additional compatible data.')
        st.markdown('[Explore ECDC Lyme borreliosis resources](https://www.ecdc.europa.eu/en/borreliosis)')
        st.caption('Discovery resource; no international numerical estimates are imported from this portal.')
    with st.expander('Sources, downloads and citation'):
        st.write('Evidence framework ' + VERSION + ' · Reviewed ' + REVIEW_DATE)
        for source in SOURCES:
            st.markdown('[' + source['citation'] + '](' + source['url'] + ')')
            st.caption(source['status'])
        st.markdown('**Suggested citation for the framework**')
        st.write(CITATION)
        st.caption('Cite original papers for their findings. This framework is software and methods, not a peer-reviewed economic estimate.')
        st.download_button('Download evidence values CSV', csv_bytes(evidence_rows()), file_name='PathwayAI_US_Burden_Evidence_v0.1.0.csv', mime='text/csv', key='us_burden_csv')
        st.download_button('Download burden inventory CSV', csv_bytes(impact_inventory()), file_name='PathwayAI_Burden_Inventory_v0.1.0.csv', mime='text/csv', key='us_burden_inventory')
        st.download_button('Download reproducible evidence package', json.dumps(evidence_package(), indent=2).encode('utf-8'), file_name='PathwayAI_Burden_Evidence_v0.1.0.json', mime='application/json', key='us_burden_package')
