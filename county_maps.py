"""Single-measure county map using checked 2024 reported Lyme rates."""
import html
import json
import re
from pathlib import Path


def rate_data():
    return json.loads((Path(__file__).resolve().parent / "data" / "ny_lyme_map_rates_2024.json").read_text())


def sorted_county_rates(order="highest"):
    """Sort actual numeric rates, with alphabetic tie-breaks; retain provenance."""
    import pandas as pd
    if order not in ("highest", "alphabetical"):
        raise ValueError("Unknown county sort order")
    data = rate_data()
    frame = pd.DataFrame([{"County": name.title(), "Reported cases per 100,000": rate,
                           "Year": 2024, "source_url": data["source_url"], "pdf_page": 5}
                          for name, rate in data["county_rates"].items()])
    columns = ["Reported cases per 100,000", "County"] if order == "highest" else ["County"]
    ascending = [False, True] if order == "highest" else [True]
    return frame.sort_values(columns, ascending=ascending).reset_index(drop=True)


def county_rate_report(order):
    frame = sorted_county_rates(order)
    label = "Highest to lowest reported rate" if order == "highest" else "Alphabetical by county"
    lines = ["New York County Lyme Rates — 2024", label,
             "Reported Lyme cases per 100,000 residents. These are rates, not case counts.",
             "57 counties; NYC is reported separately as an aggregate and is excluded here.",
             "", "COUNTY | REPORTED CASES PER 100,000"]
    lines += [f"{row['County']} | {row['Reported cases per 100,000']:,.1f}" for row in frame.to_dict("records")]
    lines += ["", "Source: NYSDOH 2024 county rates PDF, page 5, Lyme column.",
              rate_data()["source_url"],
              "Reported surveillance rates are not tick density or a prediction of personal infection risk."]
    return "\n".join(lines)


def county_key(name):
    return re.sub(r"[^a-z]", "", str(name).lower())


def rate_color(rate, maximum):
    if rate is None:
        return "#bebebe"
    intensity = max(0, min(rate / maximum, 1))
    rgb = [round(light + (dark - light) * intensity) for light, dark in zip((235, 243, 248), (20, 75, 115))]
    return "#" + "".join(f"{value:02x}" for value in rgb)


def show_lyme_rate_map(boundaries, geom_paths, project, note):
    import pandas as pd
    import streamlit as st
    import streamlit.components.v1 as components

    data = rate_data()
    rates = {county_key(name): rate for name, rate in data["county_rates"].items()}
    maximum = max(rates.values())
    bounds = (-79.9, 40.35, -71.7, 45.15)
    width, height = 760, 420
    parts = [f'<svg role="img" aria-label="Reported Lyme cases per 100,000 residents, New York 2024" viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"><title>Reported Lyme rates, 2024: darker blue means higher reported rate</title><rect width="100%" height="100%" fill="white"/>']
    for feature in boundaries["features"]:
        name = feature["properties"].get("NAME", "")
        rate = rates.get(county_key(name))
        description = f"{name}: {rate:g} reported cases per 100,000, 2024" if rate is not None else f"{name}: NYC aggregate reported separately"
        for path in geom_paths(feature["geometry"], bounds, width, height):
            parts.append(f'<path d="{path}" fill="{rate_color(rate, maximum)}" stroke="#6b7280" stroke-width="0.8"><title>{html.escape(description)}</title></path>')
    for fid, label, color, lon, lat in (("36027", "Dutchess", "#2474A6", -73.74, 41.76),
                                       ("36071", "Orange", "#C65D17", -74.31, 41.41)):
        for feature in boundaries["features"]:
            if str(feature.get("id", "")).zfill(5) == fid:
                for path in geom_paths(feature["geometry"], bounds, width, height):
                    parts.append(f'<path d="{path}" fill="none" stroke="white" stroke-width="4"/><path d="{path}" fill="none" stroke="{color}" stroke-width="2"><title>{label} comparison county</title></path>')
        x, y = project(lon, lat, bounds, width, height)
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" stroke="white" stroke-width="1" paint-order="stroke" font-size="18">★<title>{label}</title></text>')
    parts.append('</svg>')
    st.write("Reported Lyme cases per 100,000 residents · 2024. Darker blue means a higher reported rate.")
    components.html('<div style="background:white;border:1px solid #d1d5db;border-radius:10px;padding:8px;height:440px">' + ''.join(parts) + '</div>', height=460)
    st.markdown(f'<div aria-label="Reported Lyme rate legend"><div style="height:16px;background:linear-gradient(to right,#ebf3f8,#144b73)"></div><div style="display:flex;justify-content:space-between"><span>0</span><span>{maximum:g} cases per 100,000</span></div></div>', unsafe_allow_html=True)
    st.write("Highlighted counties: Dutchess and Orange. Gray areas belong to the separate NYC summary.")
    with st.expander("Download statewide reported-rate map data"):
        from report_download import branded_download_button
        st.write("Choose a PDF sorted by reported rate or by county name. Both contain the same 2024 data.")
        high, alpha = st.columns(2)
        for col, order, label in [(high, "highest", "Download PDF · highest rate first"),
                                  (alpha, "alphabetical", "Download PDF · county A–Z")]:
            with col:
                branded_download_button(label, county_rate_report(order).encode("utf-8"),
                                        file_name=f"NY_Lyme_Rates_2024_{order}.txt", mime="text/plain",
                                        key="ny_lyme_rates_pdf_" + order)
        with st.expander("Spreadsheet copies (CSV)"):
            for order, label in [("highest", "Download CSV · highest rate first"),
                                 ("alphabetical", "Download CSV · county A–Z")]:
                st.download_button(label, sorted_county_rates(order).to_csv(index=False).encode("utf-8-sig"),
                                   file_name=f"NY_Lyme_Rates_2024_{order}.csv", mime="text/csv",
                                   key="ny_lyme_rates_csv_" + order)
    note("Lyme map source: supplied NYSDOH 2024 rates PDF, page 5, county Lyme column. Shading represents reported human case rates, "
         "not tick density or personal infection risk. NYC is a single source aggregate; its rate is not assigned to individual borough counties. "
         "Dutchess is not the highest reported-rate county in this table. Tick observations are a separate map view. "
         "[NYSDOH county rates](https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf)")
