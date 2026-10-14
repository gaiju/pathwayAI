"""Transparent scenario arithmetic; no fitted model or survey-derived mean."""

import math

CASE_SOURCE = "https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf"
RATE_SOURCE = "https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf"
COST_SOURCE = "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880"
COUNTIES = (
    ("Dutchess", 1060, 355.5),
    ("Orange", 964, 237.0),
)


def county_scenario(disseminated_share=None):
    """None selects the published overall mean, not a zero case-mix assumption."""
    if disseminated_share is not None:
        if isinstance(disseminated_share, bool) or not math.isfinite(disseminated_share) or not 0 <= disseminated_share <= 1:
            raise ValueError("Assumed share must be between zero and one")
        unit = (1 - disseminated_share) * 695 + disseminated_share * 6833
        basis = "Assumed case mix; not observed county distribution"
    else:
        unit = 2227
        basis = "Published overall medical episode mean applied uniformly"
    return [{
        "County": county, "Reported cases · 2024": cases,
        "Reported cases per 100,000 · 2024": rate,
        "Medical reference per episode · 2022 USD": round(unit, 2),
        "Illustrative medical amount · 2022 USD": round(cases * unit, 2),
        "Illustrative amount per 100,000 · 2022 USD": round(rate * unit, 2),
        "scenario_type": "illustrative_not_measured_county_cost",
        "basis": basis, "assumed_disseminated_share": disseminated_share,
        "case_source": CASE_SOURCE, "rate_source": RATE_SOURCE, "cost_source": COST_SOURCE,
        "formula": "reported cases * medical episode reference",
        "per_100000_formula": "reported cases per 100000 * medical episode reference",
        "limits": "Published reference population differs; no inflation, local case-mix, underreporting, pharmacy, causal delay or savings adjustment; OOP not added to medical cost",
    } for county, cases, rate in COUNTIES]


def show_county_cost_scenario(note):
    import pandas as pd
    import streamlit as st

    st.markdown("### Explore a county Lyme burden scenario")
    st.write("Start with reported cases. Apply one published medical-cost reference. "
             "Compare the result across counties using the same assumptions.")
    st.write("**Illustrative scenario—not measured county spending or predicted savings.**")
    basis = st.radio("Medical-cost assumption", ["Published overall mean", "Assumed localized/disseminated mix"],
                     key="county_cost_basis", horizontal=True)
    share = None
    if basis == "Assumed localized/disseminated mix":
        percent = st.selectbox("Assumed disseminated share · choose a scenario, not a diagnosis",
                               ["Choose an assumption", 0, 25, 50, 75, 100], key="county_cost_share",
                               format_func=lambda value: value if isinstance(value, str) else f"{value}%")
        st.write("Localized reference: $695. Disseminated reference: $6,833. "
                 "These are study-group means in 2022 dollars. Actual county case mix is unknown.")
        if isinstance(percent, str):
            st.info("Choose a share to calculate this scenario, or use the overall mean.")
            return
        share = percent / 100
    frame = pd.DataFrame(county_scenario(share))
    columns = [key for key in frame.columns if not key[0].islower()]
    st.dataframe(frame[columns], hide_index=True, use_container_width=True)
    st.bar_chart(frame.set_index("County")[["Illustrative medical amount · 2022 USD"]])
    st.write("The total follows reported case counts. The per-100,000 figure follows reported rates. "
             "Neither shows differences in actual local prices or spending.")
    st.write("**Patient-paid medical references:** Yu reports an overall mean of $188 "
             "among records with out-of-pocket information; localized $107 and disseminated $401. "
             "These are published study references, not PathwayAI survey averages. "
             "Patient payments are already included in total medical spending.")
    with st.expander("Survey benchmark and local reporting"):
        st.write("The supplied survey summary does not support a mean payment amount. "
                 "An average needs payment amounts, matching periods, missing-answer rules "
                 "and duplicate checks. Secure, consent-based local reporting is in development.")
    st.download_button("Download county burden scenario and sources", frame.to_csv(index=False).encode("utf-8-sig"),
                       file_name="PathwayAI_Illustrative_CountyBurden.csv", mime="text/csv", key="county_burden_csv")
    note(f"Scenario sources: [NYSDOH cases]({CASE_SOURCE}), [rates]({RATE_SOURCE}), "
         f"[Yu medical-cost reference]({COST_SOURCE}). Values inherit the existing application references; "
         "original table verification remains required. Case year 2024; cost dollar year 2022. "
         "No delay-to-disease progression model, local price estimate, survey average or savings is inferred.")
