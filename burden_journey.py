"""Public study comparisons: separate populations, outcomes and cost perspectives."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def study_comparison():
    hook = json.loads((BASE / "data/hook_2022_article_verification.json").read_text())
    means = hook["societal_group_means"]
    return [
        {"Illness group": "Confirmed localized Lyme disease", "Mean societal cost (2016 USD)": means["confirmed_localized"], "Source": hook["source_url"]},
        {"Illness group": "Confirmed disseminated Lyme disease", "Mean societal cost (2016 USD)": means["confirmed_disseminated"], "Source": hook["source_url"]},
    ]


def action_rows():
    return [
        {"Situation": "Planning time outdoors", "PathwayAI offers": "Prevention information and a downloadable preparation plan", "Community opportunity": "Share prevention education through websites and local events"},
        {"Situation": "Tick found; illness may or may not develop", "PathwayAI offers": "Removal information and guidance on contacting a clinician", "Community opportunity": "Make reliable tick-bite information easy to reach"},
        {"Situation": "Seeking evaluation or treatment", "PathwayAI offers": "Care resources, mixed-language notes and a reviewed visit summary", "Community opportunity": "Support affordable-care navigation and interpreter access"},
        {"Situation": "Ongoing symptoms or activity limitations", "PathwayAI offers": "Dated records of daily function, work changes and caregiving", "Community opportunity": "Connect residents with follow-up and practical support"},
        {"Situation": "Longer-term support needs", "PathwayAI offers": "Organized records and benefits-preparation resources", "Community opportunity": "Connect residents with qualified benefits advisers and existing services"},
    ]


def journey_svg():
    local, disseminated = [r["Mean societal cost (2016 USD)"] for r in study_comparison()]
    local_width = round(570 * local / disseminated)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="780" viewBox="0 0 1200 780" role="img" aria-labelledby="title desc">
<title id="title">How Lyme disease burden can change</title>
<desc id="desc">Hook study mean societal cost: localized disease {local} dollars; disseminated disease {disseminated} dollars, in 2016 dollars. Separate boxes describe no illness, ongoing symptoms and longer-term support. This is not a progression or a risk prediction.</desc>
<rect width="1200" height="780" rx="24" fill="#102039"/>
<g font-family="Arial, sans-serif" fill="#f7f9fc">
<text x="48" y="66" font-size="34" font-weight="700">Different situations, different support needs</text>
<text x="48" y="105" font-size="22" fill="#9bdceb">Different situations. Different needs. Opportunities to help.</text>
<rect x="40" y="134" width="1120" height="304" rx="16" fill="#203550"/>
<text x="64" y="174" font-size="24" font-weight="700">Two illness groups in the same cost study</text>
<text x="64" y="206" font-size="19" fill="#ced9e8">Mean societal cost per case · medical, nonmedical and productivity costs</text>
<text x="64" y="259" font-size="22">Localized disease</text>
<rect x="380" y="232" width="{local_width}" height="40" rx="6" fill="#86d7e9"/>
<text x="{395+local_width}" y="260" font-size="26" font-weight="700">${local:,}</text>
<text x="64" y="326" font-size="22">Disseminated disease</text>
<rect x="380" y="298" width="570" height="40" rx="6" fill="#f3c65a"/>
<text x="965" y="327" font-size="26" font-weight="700">${disseminated:,}</text>
<text x="64" y="379" font-size="19" fill="#ced9e8">Hook et al., 2022 · 2016 U.S. dollars · study averages, not expected bills</text>
<text x="64" y="411" font-size="19" fill="#ced9e8">Group differences do not establish savings from earlier treatment.</text>
<text x="48" y="482" font-size="24" font-weight="700">Other situations need their own evidence</text>
<rect x="40" y="504" width="356" height="160" rx="14" fill="#203550"/>
<rect x="422" y="504" width="356" height="160" rx="14" fill="#203550"/>
<rect x="804" y="504" width="356" height="160" rx="14" fill="#203550"/>
<g font-size="22" font-weight="700" fill="#9bdceb">
<text x="62" y="544">No illness develops</text>
<text x="444" y="544">Ongoing symptoms</text>
<text x="826" y="544">Longer-term support</text></g>
<g font-size="20">
<text x="62" y="582">Expenses vary; a tick bite</text><text x="62" y="613">does not automatically</text><text x="62" y="644">mean a zero-cost event.</text>
<text x="444" y="582">Follow-up, work and daily</text><text x="444" y="613">function matter. Symptoms</text><text x="444" y="644">alone are not disability.</text>
<text x="826" y="582">Needs and eligibility vary.</text><text x="826" y="613">No single disability cost</text><text x="826" y="644">is assigned here.</text></g>
<text x="48" y="707" font-size="19" fill="#ced9e8">These are distinct situations, not an inevitable sequence or a prediction of individual risk.</text>
<text x="48" y="746" font-size="18" fill="#9bdceb">PathwayAI · Making the Hidden Patient Journey Visible—and Actionable</text>
</g></svg>'''


def journey_text():
    rows = study_comparison()
    lines = ["HOW LYME DISEASE BURDEN CAN CHANGE", "Same-study comparison: Hook et al. (2022)"]
    for row in rows:
        lines.append(f'{row["Illness group"]}: mean societal cost USD {row["Mean societal cost (2016 USD)"]:,}, in 2016 dollars.')
    lines += ["Societal costs include medical, nonmedical and productivity components; do not add these components again.",
              "Study averages are not individual expected bills. Disseminated disease and delayed treatment are not interchangeable labels. The group difference does not establish causal savings from earlier treatment.",
              "Tick bite without illness: expenses vary; no fixed cost is assigned.",
              "Horn et al. (2025): 55 of 253 returning participants reported ongoing symptoms around three months; 466 cases enrolled. Selected follow-up participants, not a disability probability.",
              "Adrion et al. (2015): within Lyme cases, symptom-related diagnosis codes were associated with USD 3,798 higher adjusted medical costs over 12 months. Historical commercially insured population; allowed amounts, not patient bills. Do not add to Hook societal costs.",
              "Johnson et al. (2014): selected persistent-illness respondents reported work and functional impacts. Survey percentages are not probabilities of disability among newly diagnosed cases.",
              "The situations are not a progression model. No transition probabilities, county disability count or single long-term cost is estimated.",
              "PRACTICAL ACTIONS"]
    for row in action_rows():
        lines.append(" | ".join(f"{k}: {v}" for k,v in row.items()))
    lines += ["SOURCES", rows[0]["Source"], "https://doi.org/10.3389/fmed.2025.1577936", "https://doi.org/10.1371/journal.pone.0116767", "https://doi.org/10.7717/peerj.322"]
    return "\n".join(lines)


def show_burden_journey():
    import streamlit as st
    from report_download import branded_download_button
    from burden_framework import csv_bytes
    st.markdown("### How the burden can change")
    st.write("PathwayAI helps people find their next step—from prevention and seeking care to managing ongoing needs—and helps communities identify where support is needed.")
    st.image(journey_svg(), use_container_width=True)
    with st.expander("Read the figure as a table"):
        st.dataframe(study_comparison(), hide_index=True, use_container_width=True)
        st.write("No illness: costs vary. Ongoing symptoms: follow-up and function matter. Longer-term support: needs and eligibility require individual assessment.")
    st.markdown("#### Where PathwayAI and communities can help")
    st.dataframe(action_rows(), hide_index=True, use_container_width=True)
    with st.expander("Supporting studies and how to interpret them"):
        st.markdown("**Hook (2022):** The two cost bars use the same study and dollar year. Localized and disseminated disease are illness groups, not measured stages of diagnostic delay.")
        st.markdown("**Horn (2025):** 55 of 253 returning participants (about 22%) reported ongoing symptoms around three months; 466 enrolled. This supports follow-up, not a long-term disability estimate.")
        st.markdown("**Adrion (2015):** Within Lyme cases, symptom-related codes were associated with 3,798 dollars higher adjusted medical costs over 12 months. These historical allowed amounts stay separate from Hook societal costs.")
        st.markdown("**Johnson (2014):** A selected persistent-illness survey documents work and functional effects. Its percentages cannot be applied to all new Lyme cases or county populations.")
        for url in [study_comparison()[0]["Source"], "https://doi.org/10.3389/fmed.2025.1577936", "https://doi.org/10.1371/journal.pone.0116767", "https://doi.org/10.7717/peerj.322"]:
            st.markdown(f"[Original paper]({url})")
    with st.expander("Download the figure and action guide"):
        st.download_button("Download burden comparison figure (SVG)", journey_svg().encode(), file_name="PathwayAI_Burden_Journey.svg", mime="image/svg+xml", key="burden_journey_svg")
        branded_download_button("Download burden and action guide (PDF)", journey_text().encode(), file_name="PathwayAI_Burden_Journey.txt", mime="text/plain", key="burden_journey_pdf")
        st.download_button("Download community actions table (CSV)", csv_bytes(action_rows()), file_name="PathwayAI_Burden_Actions.csv", mime="text/csv", key="burden_journey_actions")
