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
        "rate_verification": "Matched user-provided NYSDOH 2024 rates PDF, page 5",
        "case_count_verification": "Inherited application count; case table still requires verification",
        "cost_verification": "Inherited publication reference; original table still requires verification",
        "formula": "reported cases * medical episode reference",
        "per_100000_formula": "reported cases per 100000 * medical episode reference",
        "limits": "Published reference population differs; no inflation, local case-mix, underreporting, pharmacy, causal delay or savings adjustment; OOP not added to medical cost",
    } for county, cases, rate in COUNTIES]


def burden_paths(county, unit_cost, annual_change=.05, years=5):
    """Hypothetical paths from a case input; no historical trend fitting."""
    if not 0 <= annual_change <= .5 or not 1 <= years <= 10 or unit_cost < 0:
        raise ValueError("Invalid scenario input")
    baseline = next(cases for name, cases, rate in COUNTIES if name == county)
    paths = []
    for label, change in (("Unchanged reported cases", 0),
                          ("Assumed lower reported cases", -annual_change),
                          ("Assumed higher reported cases", annual_change)):
        for year in range(years + 1):
            cases = baseline * (1 + change) ** year
            paths.append({"County": county, "Scenario year": year, "Scenario": label,
                          "Assumed reported cases": cases,
                          "Illustrative medical amount · 2022 USD": cases * unit_cost,
                          "Annual change assumption": change,
                          "evidence_type": "hypothetical_projection_not_forecast",
                          "baseline_case_year": 2024})
    return paths


def show_burden_paths(frame, note):
    import altair as alt
    import pandas as pd
    import streamlit as st

    with st.expander("Explore how community burden could change"):
        st.write("**Illustrative future paths · selected assumptions**")
        county = st.selectbox("County for the scenario chart", [name for name, _, _ in COUNTIES], key="burden_path_county")
        change = st.slider("Assumed annual change in reported cases (%)", 0, 20, 5, key="burden_path_change")
        unit = float(frame.loc[frame["County"] == county, "Medical reference per episode · 2022 USD"].iloc[0])
        paths = pd.DataFrame(burden_paths(county, unit, change / 100))
        chart = alt.Chart(paths).mark_line(strokeDash=[6, 4], point=True).encode(
            x=alt.X("Scenario year:Q", axis=alt.Axis(tickMinStep=1), title="Scenario years after baseline input"),
            y=alt.Y("Illustrative medical amount · 2022 USD:Q", title="Illustrative medical amount · 2022 USD", axis=alt.Axis(format="~s")),
            color=alt.Color("Scenario:N", title="Assumptions"),
            tooltip=["County:N", "Scenario:N", "Scenario year:Q",
                     alt.Tooltip("Assumed reported cases:Q", format=",.1f"),
                     alt.Tooltip("Illustrative medical amount · 2022 USD:Q", format=",.0f")],
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.write("Year 0 uses the 2024 case input. Years 1–5 apply your selected annual change and a fixed medical-cost reference.")
        note("Future paths are hypothetical, not a validated prediction or recorded time trend. No inflation or intervention effect is estimated. "
             "Lower reported counts could reflect disease, diagnosis or reporting changes. The gap between lines is not PathwayAI savings.")
        st.download_button("Download hypothetical paths and assumptions", paths.to_csv(index=False).encode("utf-8-sig"),
                           file_name="PathwayAI_Hypothetical_BurdenPaths.csv", mime="text/csv", key="burden_path_csv")


def show_county_cost_scenario(note):
    import pandas as pd
    import streamlit as st

    st.markdown("#### County medical-cost scenarios")
    st.write("Start with reported cases. Apply one published medical-cost reference. "
             "Compare the result across counties using the same assumptions.")
    st.write("**Illustrative calculation · reported cases × study cost reference**")
    note("County cost scenarios are illustrative arithmetic, not measured county spending, predicted bills or savings.")
    basis = st.radio("Medical-cost assumption", ["Published overall mean", "Assumed localized/disseminated mix"],
                     key="county_cost_basis", horizontal=True)
    share = None
    if basis == "Assumed localized/disseminated mix":
        percent = st.selectbox("Assumed share of disseminated cases",
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
    st.write("Compare totals and amounts per 100,000 residents using the same cost reference.")
    st.write("**Patient-paid medical references:** Yu reports an overall mean of $188 "
             "among records with out-of-pocket information; localized $107 and disseminated $401. "
             "These are published study references. "
             "Patient payments are already included in total medical spending.")
    with st.expander("Survey benchmark and local reporting"):
        st.write("Local averages require reviewed payment amounts over matching periods, with duplicate checks and secure, consent-based reporting.")
    note("Published patient-paid costs are not PathwayAI survey averages. The supplied survey summary does not support a mean payment amount. Secure shared collection remains in development.")
    st.download_button("Download county burden scenario and sources", frame.to_csv(index=False).encode("utf-8-sig"),
                       file_name="PathwayAI_Illustrative_CountyBurden.csv", mime="text/csv", key="county_burden_csv")
    show_burden_paths(frame, note)
    note(f"Scenario sources: [NYSDOH cases]({CASE_SOURCE}), [rates]({RATE_SOURCE}), "
         f"[Yu medical-cost reference]({COST_SOURCE}). Rates were matched to the user-provided NYSDOH 2024 PDF, page 5. Case counts and cost values inherit existing application references; "
         "original table verification remains required. Case year 2024; cost dollar year 2022. "
         "No delay-to-disease progression model, local price estimate, survey average or savings is inferred.")
