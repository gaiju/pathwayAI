"""Observed reported-rate series from checked public PDFs, separate from scenarios."""
import json
from pathlib import Path


def county_rate_trend():
    data = Path(__file__).resolve().parent / "data"
    regional = json.loads((data / "mid_hudson_lyme_rates_verification.json").read_text())
    latest = json.loads((data / "ny_lyme_rates_2024_verification.json").read_text())
    rows = []
    for year, rates in regional["rates"].items():
        for county, rate in rates.items():
            rows.append({"Year": int(year), "Area": county, "Reported cases per 100,000": rate,
                         "source_url": regional["source_url"], "pdf_page": 219,
                         "evidence_type": "reported_surveillance_rate"})
    for county, rate in latest["verified_rates"].items():
        rows.append({"Year": 2024, "Area": "New York State" if county == "NYS TOTAL" else county,
                     "Reported cases per 100,000": rate, "source_url": latest["source_url"],
                     "pdf_page": 5, "evidence_type": "reported_surveillance_rate"})
    return rows


def show_county_rate_trend(note):
    import altair as alt
    import pandas as pd
    import streamlit as st

    st.markdown("### Reported Lyme rates over time")
    st.write("Dutchess, Orange and New York State · 2022–2024 · cases per 100,000 residents.")
    frame = pd.DataFrame(county_rate_trend())
    chart = alt.Chart(frame).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Reporting year"),
        y=alt.Y("Reported cases per 100,000:Q", title="Reported cases per 100,000", scale=alt.Scale(zero=True)),
        color=alt.Color("Area:N", title=None, scale=alt.Scale(
            domain=["Dutchess", "Orange", "New York State"], range=["#2474A6", "#C65D17", "#6B7280"])),
        tooltip=["Area:N", "Year:O", alt.Tooltip("Reported cases per 100,000:Q", format=".1f")],
    ).properties(height=290)
    st.altair_chart(chart, use_container_width=True)
    with st.expander("Download reported-rate trend and sources"):
        st.download_button("Download reported rates · 2022–2024", frame.to_csv(index=False).encode("utf-8-sig"),
                           file_name="Dutchess_Orange_Reported_Lyme_Rates_2022_2024.csv",
                           mime="text/csv", key="county_rate_trend_csv")
    note("Observed-rate chart: 2022–2023 values checked against Mid-Hudson CHA 2025 Figure 147, printed/PDF p. 219; "
         "2024 values checked against NYSDOH rates PDF p. 5. The 2022 surveillance case-definition change makes pre-2022 rates noncomparable; "
         "only 2022 onward is plotted. Reported rates reflect surveillance and may change with diagnosis, reporting and population as well as disease frequency. "
         "This is not a prediction, personal-risk estimate or evidence of PathwayAI's effect. "
         "[Regional assessment](https://www.dutchessny.gov/Departments/DBCH/Docs/MHRCHA2025.pdf) · "
         "[NYSDOH 2024 rates](https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf)")
