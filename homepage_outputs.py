"""Public sample downloads, isolated from patient session state and AI services."""
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def sample_patient_pdf():
    from pdf_report import report_pdf
    visit=(BASE/'submission/PathwayAI_Fictional_Visit_Summary.txt').read_text()
    text=visit+'\n\nILLUSTRATIVE HOUSEHOLD BURDEN\nReporting period: Past 30 days\nMoney paid for care: $180\nTravel spending: $45\nRecorded spending total: $225\nWorkdays missed: 3\nUnpaid caregiving: 8 hours\nWorkdays and caregiving hours remain separate from spending.\n\nNEXT CONVERSATION\nAsk the provider about fees, coverage and financial assistance.\nKeep original test reports for the clinician to review.\nThis fictional sample is not a benefits determination or clinical validation.\n'
    return report_pdf(text,footer_label='PathwayAI | Fictional sample — not a real patient record')


def sample_county_pdf():
    # Refresh helper imports and key the public sample by report version, so a
    # warm Streamlit process cannot keep serving the previous report layout.
    from community_runtime import ensure_current_community_modules
    ensure_current_community_modules()
    from county_burden_report import REPORT_VERSION
    return _sample_county_pdf(REPORT_VERSION)


@lru_cache(maxsize=2)
def _sample_county_pdf(report_version):
    from county_burden_report import build_report
    from county_brief_pdf import county_brief_pdf
    return county_brief_pdf(build_report('Dutchess','Getting to care',False))


def show_homepage_outputs():
    import streamlit as st
    st.subheader('See how PathwayAI can help')
    family,community=st.columns(2)
    with family:
        st.markdown('**Prepare for care and benefits conversations**')
        st.write('Organize your story, costs and daily-life impacts for appointments and support discussions—including preparation for a disability application, if relevant.')
        st.download_button('View sample patient summary (PDF)',sample_patient_pdf(),file_name='PathwayAI_Fictional_Patient_Summary.pdf',mime='application/pdf',key='home_sample_patient')
        st.caption('Fictional example · no form or personal information needed. Your personal record supplements medical and other required documentation; each program determines eligibility and documentation requirements.')
    with community:
        st.markdown('**Prepare for a community planning meeting**')
        st.write('Bring local Lyme data, healthcare-access context and a source-linked planning question to a team meeting or support discussion.')
        st.download_button('View sample county brief (PDF)',sample_county_pdf(),file_name='PathwayAI_Dutchess_Sample_County_Brief.pdf',mime='application/pdf',key='home_sample_county')
        st.caption('Dutchess County example · study-based costs, not measured local spending.')
    with st.expander('Improved through feedback'):
        st.markdown('- **Saved records:** navigation checks verify that entered costs remain available when moving between sections and editing another field.\n- **Multilingual downloads:** English-, Chinese- and Russian-speaking testers helped identify usability and PDF-character issues.\n- **County briefs:** clearer planning points, numbered citations and references collected at the end.')
        st.caption('These describe subsequent improvements and focused testing, not clinical validation or demonstrated savings. Personal records remain separate from community evidence.')
