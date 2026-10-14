"""Authored fictional cohort, never connected to patient files or AI inputs."""

import csv
import io
from statistics import median


def fictional_cards():
    return [{
        "id": f"EXAMPLE-{index + 1}", "residence_fips": "36027",
        "residence": "Dutchess County, New York",
        "possible_exposure": "Orange County, New York" if index == 1 else "Dutchess County, New York",
        "period": "Past 30 days", "phase": "Before diagnosis",
        "medical_oop": (100, 250, 400, 300, 200, None)[index],
        "other_oop": (10, 50, 75, 25, 80, None)[index],
        "workdays": (1, 2, 3, 4, 5, None)[index],
        "caregiver_hours": (2, 4, 6, 8, 10, None)[index],
        "barrier": "Transportation / distance" if index < 5 else None,
        "evidence_type": "Synthetic demonstration; invented, not collected",
    } for index in range(6)]


def aggregate_demo(cards):
    """Match production pilot grouping and suppression, using fictional data only."""
    cohort = [card for card in cards if card["residence_fips"] == "36027"
              and card["period"] == "Past 30 days" and card["phase"] == "Before diagnosis"]
    rows = []
    for field, label in (("medical_oop", "Medical OOP band"),
                         ("other_oop", "Other OOP band"), ("barrier", "Care barrier")):
        values = [card[field] for card in cohort if card[field] is not None]
        if field != "barrier":
            values = ["$0" if v == 0 else "Under $100" if v < 100 else
                      "$100–$499" if v < 500 else "$500 or more" for v in values]
        counts = {value: values.count(value) for value in set(values)}
        shown = "; ".join(f"{value}: {counts[value]} examples" for value in sorted(counts))
        if len(values) < 5 or any(count < 5 for count in counts.values()):
            shown = "Withheld: insufficient responses or a small category"
        rows.append({"Measure": label, "Synthetic result": shown,
                     "Usable examples": len(values)})
    for field, label in (("workdays", "Median missed workdays"),
                         ("caregiver_hours", "Median unpaid caregiver hours")):
        values = [card[field] for card in cohort if card[field] is not None]
        rows.append({"Measure": label,
                     "Synthetic result": str(median(values)) if len(values) >= 5 else "Withheld: fewer than 5 usable examples",
                     "Usable examples": len(values)})
    return rows


def demo_summary_csv(rows):
    output = io.StringIO()
    columns = ["evidence_type", "county", "period", "phase", "Measure", "Synthetic result", "Usable examples"]
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row, evidence_type="SYNTHETIC; invented, not collected",
                             county="Dutchess County, New York", period="Past 30 days",
                             phase="Before diagnosis"))
    return output.getvalue().encode("utf-8-sig")


def show_burden_pathway_demo(simple=True):
    import streamlit as st

    st.markdown("### From individual experience to community priorities")
    st.write("Spending, missed work and unpaid care reveal burdens that case counts alone cannot show.")
    st.write("**SYNTHETIC DEMONSTRATION — six invented cards, not collected patient reports or actual county findings.**")
    st.markdown("**Reviewed burden card → comparable community summary → support to evaluate**")
    cards = fictional_cards()
    choice = st.selectbox("Explore a fictional burden card", [card["id"] for card in cards], key="burden_demo_card")
    card = next(card for card in cards if card["id"] == choice)
    with st.container(border=True):
        st.write(f"**{card['id']} · FICTIONAL CARD**")
        st.write(f"Residence: {card['residence']} · Possible exposure: {card['possible_exposure']}")
        st.write("Period: past 30 days · Journey phase: before diagnosis")
        st.write("A person would review the fields and choose whether to contribute. This example is not a real consent record.")
        medical, other = card["medical_oop"], card["other_oop"]
        paid = medical + other if medical is not None and other is not None else None
        first, second, third = st.columns(3)
        first.metric("Fictional recorded spending", "Not reported" if paid is None else f"${paid:,}",
                     help="Medical plus other patient-paid spending; excludes modeled work loss.")
        second.metric("Fictional missed workdays", card["workdays"] if card["workdays"] is not None else "Not reported")
        third.metric("Fictional caregiver hours", card["caregiver_hours"] if card["caregiver_hours"] is not None else "Not reported")
        st.write("Money paid for care: " + ("Not reported" if medical is None else f"${medical:,}") +
                 " · Other money paid: " + ("Not reported" if other is None else f"${other:,}"))
    st.markdown("**Synthetic summary of all six cards · Dutchess residence · same phase and period**")
    rows = aggregate_demo(cards)
    if simple:
        st.write("**Five fictional cards report transport as a care barrier.** Their middle "
                 "(median) values are 3 missed workdays and 6 hours of unpaid care.")
        with st.expander("See the fictional cost bands and time summary"):
            st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    st.write("Five cards contain usable cost and time fields; one leaves them unknown. "
             "Missing answers stay missing. Selecting a card changes only the preview, not the cohort.")
    st.write("**Response to evaluate:** transport navigation. **Check:** appointments completed, "
             "patient-paid travel spending and support still needed. Confirm actual participant needs before allocating resources.")
    st.download_button("Download synthetic community summary", demo_summary_csv(rows),
                       file_name="PathwayAI_SYNTHETIC_CommunitySummary.csv", mime="text/csv",
                       key="burden_demo_summary")
    with st.expander("How the demonstration differs from real collection"):
        st.write("This fixed fictional cohort is not a live reporting system. It reads no patient "
                 "files, sends nothing to AI and saves no contributions. Real collection needs "
                 "reviewed consent, private durable storage, duplicate handling, retention rules "
                 "and privacy-reviewed publication. A minimum count alone is not sufficient protection.")
        st.write("Production pilot summaries group by residence, reporting period and journey phase. "
                 "Cost bands and categories are withheld when a category is small; time medians need "
                 "five usable responses. Exposure location is separate from residence. Voluntary "
                 "reports do not establish county prevalence, causal savings or intervention effects.")
