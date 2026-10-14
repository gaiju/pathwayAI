"""Transparent scenario arithmetic; no fitted model or survey-derived mean."""

import math
import json
from pathlib import Path

CASE_SOURCE = "https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf"
RATE_SOURCE = "https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf"
COST_SOURCE = "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880"
HOOK_SOURCE = "https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article"
COUNTIES = (
    ("Dutchess", 1060, 355.5),
    ("Orange", 964, 237.0),
)


def county_cost_categories():
    """Decompose the same societal mean; do not add overlapping patient costs."""
    hook = json.loads((Path(__file__).resolve().parent / "data" / "hook_2022_article_verification.json").read_text())
    medical = hook["societal_medical_mean"]
    other_and_productivity = hook["societal_mean"] - medical
    return [{"County": county, "Reported cases · 2024": cases,
             "Reported cases per 100,000 · 2024": rate,
             "Medical costs · 2016 USD": cases * medical,
             "Other expenses and lost productivity · 2016 USD": cases * other_and_productivity,
             "Estimated societal total · 2016 USD": cases * hook["societal_mean"],
             "source_url": HOOK_SOURCE, "case_source_url": CASE_SOURCE,
             "medical_reference_per_participant": medical,
             "other_and_productivity_reference_per_participant": other_and_productivity,
             "dollar_year": 2016, "evidence_type": "study_based_county_illustration",
             "method": "Reported cases times weighted societal reference; other expenses plus productivity is societal mean minus medical mean, not a separately reported average",
             "scope": "Assumed transfer of study experience to reported county cases; not measured county spending. Other expenses and productivity cannot be separately valued from supplied overall results. Survey findings are contextual, not added as dollar amounts."}
            for county, cases, rate in COUNTIES]


def county_scenario(disseminated_share=None, perspective="medical"):
    """None selects the published overall mean, not a zero case-mix assumption."""
    if perspective not in ("medical", "societal"):
        raise ValueError("Choose medical or societal perspective")
    if perspective == "societal" and disseminated_share is not None:
        raise ValueError("Societal illustration uses the overall study mean including probable cases")
    if perspective == "societal":
        unit = 2032
        basis = "Hook overall societal mean applied uniformly; includes medical, nonmedical and productivity"
    elif disseminated_share is not None:
        if isinstance(disseminated_share, bool) or not math.isfinite(disseminated_share) or not 0 <= disseminated_share <= 1:
            raise ValueError("Assumed share must be between zero and one")
        unit = (1 - disseminated_share) * 695 + disseminated_share * 6833
        basis = "Assumed case mix; not observed county distribution"
    else:
        unit = 2227
        basis = "Published overall medical episode mean applied uniformly"
    dollar_year = 2016 if perspective == "societal" else 2022
    reference_column = ("Societal reference per participant" if perspective == "societal" else "Medical reference per episode") + f" · {dollar_year} USD"
    amount_column = ("Illustrative societal amount" if perspective == "societal" else "Illustrative medical amount") + f" · {dollar_year} USD"
    return [{
        "County": county, "Reported cases · 2024": cases,
        "Reported cases per 100,000 · 2024": rate,
        reference_column: round(unit, 2),
        amount_column: round(cases * unit, 2),
        f"Illustrative amount per 100,000 · {dollar_year} USD": round(rate * unit, 2),
        "scenario_type": "illustrative_not_measured_county_cost",
        "basis": basis, "assumed_disseminated_share": disseminated_share,
        "case_source": CASE_SOURCE, "rate_source": RATE_SOURCE, "cost_source": HOOK_SOURCE if perspective == "societal" else COST_SOURCE,
        "cost_perspective": perspective, "dollar_year": dollar_year,
        "rate_verification": "Matched user-provided NYSDOH 2024 rates PDF, page 5",
        "case_count_verification": "Matched user-provided NYSDOH 2024 case-count PDF, page 5, on 2026-10-14",
        "cost_verification": "Hook Results checked against user-supplied article text on 2026-10-14" if perspective == "societal" else "Inherited publication reference; original table still requires verification",
        "formula": "reported cases * study cost reference",
        "per_100000_formula": "reported cases per 100000 * study cost reference",
        "limits": "Study population differs; no inflation, local case-mix, underreporting or savings adjustment. OOP not added to total medical or societal cost; work loss not added again to societal cost. Hook excludes suspected, undiagnosed and nonacute disease; Yu excludes pharmacy.",
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


def show_county_burden_comparison(note):
    """Main two-county illustration with separate, unextrapolated survey context."""
    import altair as alt
    import pandas as pd
    import streamlit as st

    st.markdown("### Estimated community cost: Dutchess and Orange")
    st.write("Study-based societal illustration · 2024 reported cases × $2,032 per participant · 2016 dollars.")
    st.write("The study reference includes medical care, other expenses and lost productivity.")
    frame = pd.DataFrame(county_scenario(perspective="societal"))
    amount = "Illustrative societal amount · 2016 USD"
    cols = st.columns(3)
    for col, (_, row) in zip(cols, frame.iterrows()):
        col.metric(row["County"] + " · societal illustration", f"${row[amount] / 1_000_000:.2f}M")
    cols[2].metric("Both counties · societal illustration", f"${frame[amount].sum() / 1_000_000:.2f}M")
    categories = pd.DataFrame(county_cost_categories())
    plot = categories.rename(columns={"Medical costs · 2016 USD": "Medical costs",
                                      "Other expenses and lost productivity · 2016 USD": "Other costs + time lost"}).melt(
                                          id_vars="County", value_vars=["Medical costs", "Other costs + time lost"],
                                          var_name="Cost category", value_name="Estimated amount")
    chart = alt.Chart(plot).mark_bar().encode(
        x=alt.X("County:N", title=None),
        y=alt.Y("Estimated amount:Q", title="Estimated societal burden · 2016 USD", axis=alt.Axis(format="$~s"), stack="zero"),
        color=alt.Color("Cost category:N", title=None, scale=alt.Scale(domain=["Medical costs", "Other costs + time lost"], range=["#2474A6", "#C65D17"]), legend=alt.Legend(orient="bottom")),
        tooltip=["County:N", "Cost category:N", alt.Tooltip("Estimated amount:Q", format="$,.0f")],
    ).properties(height=260)
    st.altair_chart(chart, use_container_width=True)
    display = categories[["County", "Reported cases · 2024", "Reported cases per 100,000 · 2024",
                          "Medical costs · 2016 USD", "Other expenses and lost productivity · 2016 USD",
                          "Estimated societal total · 2016 USD"]].copy()
    for column in ("Medical costs · 2016 USD", "Other expenses and lost productivity · 2016 USD", "Estimated societal total · 2016 USD"):
        display[column] = display[column].map(lambda value: f"${value:,.0f}")
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button("Download two-county burden comparison", categories.to_csv(index=False).encode("utf-8-sig"),
                       file_name="Dutchess_Orange_Societal_Burden_Illustration.csv", mime="text/csv", key="county_burden_comparison_csv")
    st.markdown("#### What patients reported · survey across locations")
    st.write("The supplied PathwayAI survey summary adds experiences of financial pressure, time lost and long waits for diagnosis.")
    survey = st.columns(3)
    survey[0].metric("Reported paying at least $10,000", "14 of 33")
    survey[1].metric("Reported more than 100 days lost", "18 of 33")
    survey[2].metric("Reported over 5 years to diagnosis", "20 of 33")
    st.write("Use the county illustration to understand scale, and these patient experiences to choose what local support needs to measure.")
    note(f"Main county illustration: verified NYSDOH 2024 case counts (Dutchess 1,060; Orange 964), cases PDF p. 5; "
         f"rates 355.5 and 237.0 per 100,000, rates PDF p. 5. Hook mean $2,032 was checked against supplied article Results; "
         f"2016 dollars, not current local prices or observed county spending. Total $4,112,768 combines these two illustrative totals only. "
         f"Societal cost already includes medical, nonmedical and productivity; patient payments and survey spending are not added again. "
         f"Reported cases do not include all infections; transferring the study mean to counties assumes a comparable case mix and cost experience. "
         f"Hook excludes suspected, undiagnosed and nonacute illness. [Case counts]({CASE_SOURCE}) · [Rates]({RATE_SOURCE}) · [Hook study]({HOOK_SOURCE})")
    note("Survey context: project lead's supplied October 3, 2026 summary of 33 self-reported diagnosed respondents across locations, "
         "not independently recalculated from raw records. Spending thresholds are not average dollar costs; days lost are not monetized. "
         "Reporting periods, question wording and denominators require confirmation. A small voluntary survey cannot be treated as representative of Dutchess or Orange. "
         "Survey percentages are not multiplied by county case counts or added to the societal illustration. Broader county burden requires consented, locally representative evidence with comparable periods.")
    note("Category breakdown: Hook's societal mean $2,032 and societal medical mean $1,333 describe the societal analysis. "
         "The remaining $699 is calculated as their difference and combines nonmedical expenses with lost productivity; it is not a separately reported component mean. "
         "The supplied article text does not provide overall means that separate those two components. Patient medical-bill means use a different analysis denominator, "
         "so they cannot be subtracted from societal totals. The survey's $10,000 threshold does not establish a medical, travel, work-loss or caregiver average; "
         "further category estimates require reported amounts and common periods, or explicitly selected scenario assumptions.")


def show_burden_paths(frame, note):
    import altair as alt
    import pandas as pd
    import streamlit as st

    with st.expander("Explore how community burden could change"):
        st.write("**Illustrative future paths · selected assumptions**")
        county = st.selectbox("County for the scenario chart", [name for name, _, _ in COUNTIES], key="burden_path_county")
        change = st.slider("Assumed annual change in reported cases (%)", 0, 20, 5, key="burden_path_change")
        reference = next(column for column in frame.columns if "reference per" in column)
        unit = float(frame.loc[frame["County"] == county, reference].iloc[0])
        paths = pd.DataFrame(burden_paths(county, unit, change / 100))
        amount = next(column for column in frame.columns if column.startswith("Illustrative ") and "amount ·" in column)
        paths = paths.rename(columns={"Illustrative medical amount · 2022 USD": amount})
        paths["cost_perspective"] = frame["cost_perspective"].iloc[0]
        paths["dollar_year"] = frame["dollar_year"].iloc[0]
        paths["cost_source"] = frame["cost_source"].iloc[0]
        paths["case_count_verification"] = frame["case_count_verification"].iloc[0]
        chart = alt.Chart(paths).mark_line(strokeDash=[6, 4], point=True).encode(
            x=alt.X("Scenario year:Q", axis=alt.Axis(tickMinStep=1), title="Scenario years after baseline input"),
            y=alt.Y(f"{amount}:Q", title=amount, axis=alt.Axis(format="~s")),
            color=alt.Color("Scenario:N", title="Assumptions"),
            tooltip=["County:N", "Scenario:N", "Scenario year:Q",
                     alt.Tooltip("Assumed reported cases:Q", format=",.1f"),
                     alt.Tooltip(f"{amount}:Q", format=",.0f")],
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.write("Year 0 uses the 2024 case input. Years 1–5 apply your selected annual change and a fixed study-cost reference.")
        note("Future paths are hypothetical, not a validated prediction or recorded time trend. No inflation or intervention effect is estimated. "
             "Lower reported counts could reflect disease, diagnosis or reporting changes. The gap between lines is not PathwayAI savings.")
        st.download_button("Download hypothetical paths and assumptions", paths.to_csv(index=False).encode("utf-8-sig"),
                           file_name="PathwayAI_Hypothetical_BurdenPaths.csv", mime="text/csv", key="burden_path_csv")


def show_county_cost_scenario(note):
    import pandas as pd
    import streamlit as st

    st.markdown("#### County burden calculations")
    st.write("Start with reported cases. Apply one published cost reference. "
             "Compare the result across counties using the same assumptions.")
    st.write("**Illustrative calculation · reported cases × study cost reference**")
    note("County cost scenarios are illustrative arithmetic, not measured county spending, predicted bills or savings.")
    choice = st.radio("Cost perspective", ["Societal burden · Hook 2022", "Medical spending · Yu 2026"], key="county_cost_perspective", horizontal=True)
    perspective = "societal" if choice.startswith("Societal") else "medical"
    basis = "Published overall mean"
    if perspective == "medical":
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
    if perspective == "societal":
        st.write("$2,032 per participant · 2016 dollars · medical care, other expenses and lost productivity.")
    frame = pd.DataFrame(county_scenario(share, perspective=perspective))
    columns = [key for key in frame.columns if not key[0].islower()]
    st.dataframe(frame[columns], hide_index=True, use_container_width=True)
    amount = next(column for column in frame.columns if column.startswith("Illustrative ") and "amount ·" in column)
    st.bar_chart(frame.set_index("County")[[amount]])
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
         f"[Hook societal reference]({HOOK_SOURCE}), [Yu medical-cost reference]({COST_SOURCE}). Rates were matched to the user-provided NYSDOH 2024 PDF, page 5. Hook costs were checked against the supplied article text; "
         "case counts were checked against the supplied NYSDOH 2024 cases PDF, page 5. Yu costs remain pending original-table verification. Case year 2024; Hook dollar year 2016; Yu dollar year 2022. "
         "No delay-to-disease progression model, local price estimate, survey average or savings is inferred.")
