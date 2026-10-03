import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="PathwayAI Beta",
    page_icon="🧭",
    layout="centered"
)

DATA_FILE = Path(__file__).with_name("pathwayAI_data.xlsx")

NY_TICK_FILE = Path(__file__).with_name("ny_tick_data.csv")

POPULATION_FILE = Path(__file__).with_name("pathwayai_population_data.csv")

@st.cache_data
def load_data():
    geography = pd.read_excel(DATA_FILE, sheet_name="Geography")
    clinical = pd.read_excel(DATA_FILE, sheet_name="Clinical_Evidence")
    return geography, clinical

@st.cache_data
def load_ny_tick_data():
    return pd.read_csv(NY_TICK_FILE)

@st.cache_data
def load_population_data():
    return pd.read_csv(POPULATION_FILE)

geography, clinical = load_data()
ny_tick_data = load_ny_tick_data()
population_data = load_population_data()


dutchess_data = ny_tick_data[
    ny_tick_data["County"].str.contains("Dutchess", case=False, na=False)
].copy()

latest_dutchess = dutchess_data.sort_values("Year", ascending=False).iloc[0]

st.title("PathwayAI")
st.caption("Making the Invisible Lyme Disease Journey Visible")

view = st.radio(
    "Choose view",
    ["Travel Intelligence", "My Journey", "Population Insights"],
    horizontal=True
)

if view == "Travel Intelligence":
    st.header("Travel Intelligence")
    st.write(
        "Explore tick-exposure context before travel using destination, season, "
        "environmental surveillance, and relevant health context."
    )
    st.subheader("Plan Your Trip")

    travel_destination = st.selectbox(
        "Where are you traveling?",
        [
            "Dutchess County, New York",
            "Chester County, Pennsylvania",
            "Carroll County, Maryland"
        ]
    )

    travel_month = st.selectbox(
        "When are you traveling?",
        [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ],
        index=5
    )

    health_context = st.multiselect(
        "Do any of these apply to you?",
        [
            "Age 65 or older",
            "Weakened immune system or immunosuppressive treatment",
            "No spleen or reduced spleen function",
            "Cancer or cancer treatment",
            "Other relevant health condition"
        ]
    )
    if st.button("Generate Travel Exposure Card", type="primary"):
        st.divider()
        st.header("My Travel Exposure Card")

        st.write(f"**Destination:** {travel_destination}")
        st.write(f"**Travel month:** {travel_month}")

        if health_context:
            st.write("**Health context:** " + ", ".join(health_context))
        else:
            st.write("**Health context:** None selected")

        if travel_destination == "Dutchess County, New York":
            st.subheader("Environmental Surveillance")

            st.write(
                f"**Latest NYSDOH surveillance year:** {int(latest_dutchess['Year'])}"
            )

            st.write(
                f"**Nymph tick population density:** {latest_dutchess['Tick Population Density']:.2f}"
            )

            st.write(
                f"**B. burgdorferi positive:** {latest_dutchess['B. burgdorferi (%)']}"
            )

            st.caption(
                "Source: New York State Department of Health deer tick surveillance. "
                "Environmental surveillance describes local tick conditions and does "
                "not estimate an individual's probability of infection."
            )
        st.subheader("My Travel Snapshot")

        st.write(f"**Destination:** {travel_destination}")
        st.write(f"**Season:** {travel_month}")

        st.write(
    "**Destination exposure context:** Local surveillance indicates "
    "meaningful tick exposure in this destination."
)

        if health_context:
            st.write("**Personal context:** " + ", ".join(health_context))
        else:
            st.write("**Personal context:** None selected")

        st.write(
    "**Action:** Use enhanced tick-bite precautions during outdoor, "
    "wooded, or brush exposure."
)
        
        st.subheader("What This Means for My Trip")

        st.write(
            "**Exposure context:** Local surveillance indicates meaningful "
            "tick exposure in this destination."
        )

        if health_context:
            st.write(
                "**Personal context:** You selected: "
                + ", ".join(health_context)
            )

        st.write(
            "**Travel guidance:** This does not mean you need to avoid the "
            "destination. Consider additional tick-bite prevention, especially "
            "during outdoor, wooded, or brush exposure."
        )

        st.write(
            "**If a tick bite occurs:** Record the date and location, remove "
            "the tick promptly, and monitor for symptoms. Seek medical "
            "evaluation for concerning symptoms."
        )

        st.caption(
            "Exposure-navigation guidance only. Environmental surveillance "
            "does not estimate your individual probability of infection."
        )
    st.stop()

if view == "Population Insights":
    st.header("Population Insights")
    st.write("Population-level Lyme disease context across pilot locations.")
    st.dataframe(population_data, width="stretch")
    st.stop()

st.info(
    "Beta prototype: evidence-grounded navigation and documentation — "
    "not diagnosis or treatment."
)

# 1. EXPOSURE CONTEXT

st.subheader("1. Exposure Context")

location = st.selectbox(
    "Where are you going or where have you recently been?",
    [
        "Dutchess County, New York",
        "Chester County, Pennsylvania",
        "Carroll County, Maryland",
    ],
)

month = st.selectbox(
    "When are you going or when were you there?",
    [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ],
    index=5,
)

# 2. PERSONAL CONTEXT

st.subheader("2. Personal Context")

age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    value=62
)

immune = st.selectbox(
    "Are you immunocompromised or do you have a relevant immune condition?",
    ["No", "Yes", "Unsure"]
)

# 3. EXPOSURE DETAILS

st.subheader("3. Exposure Details")

tick_bite = st.selectbox(
    "Did you have a tick bite?",
    ["No", "Yes", "Unsure"],
    index=1
)

attachment = st.selectbox(
    "Approximate attachment duration",
    ["Unsure", "<24 hours", "24–36 hours", ">36 hours"]
)

# 4. SYMPTOMS

st.subheader("4. Symptoms")

rash = st.checkbox("New or expanding rash")
fever = st.checkbox("Fever", value=True)
fatigue = st.checkbox("Fatigue", value=True)
headache = st.checkbox("Headache")
pain = st.checkbox("Muscle or joint pain")

symptoms = []

if rash:
    symptoms.append("New or expanding rash")
if fever:
    symptoms.append("Fever")
if fatigue:
    symptoms.append("Fatigue")
if headache:
    symptoms.append("Headache")
if pain:
    symptoms.append("Muscle or joint pain")

# 5. FUNCTIONAL IMPACT & DISABILITY

st.subheader("5. Functional Impact & Disability")

daily_function = st.selectbox(
    "How much has your condition affected your usual daily activities?",
    [
        "No limitation",
        "Some limitation",
        "Major limitation",
        "Unable to perform usual activities"
    ]
)

work_impact = st.selectbox(
    "Has your condition affected your work or school?",
    [
        "No impact",
        "Reduced hours",
        "Missed work or school",
        "Stopped working or school",
        "On disability",
        "Not applicable"
    ]
)

days_missed = st.number_input(
    "Approximately how many work or school days have you missed?",
    min_value=0,
    max_value=3650,
    value=0
)

# 6. PATIENT JOURNEY & ECONOMIC BURDEN

st.subheader("6. Patient Journey & Economic Burden")

diagnostic_delay = st.selectbox(
    "How long did it take from your first symptoms to a Lyme disease diagnosis?",
    [
        "No diagnosis yet",
        "Less than 1 month",
        "1–3 months",
        "4–6 months",
        "7–12 months",
        "More than 1 year"
    ]
)

providers_seen = st.number_input(
    "Approximately how many healthcare professionals have you seen for these symptoms?",
    min_value=0,
    max_value=100,
    value=0
)

oop_cost = st.selectbox(
    "Approximately how much have you paid out of pocket related to this illness?",
    [
        "$0–$499",
        "$500–$999",
        "$1,000–$4,999",
        "$5,000–$9,999",
        "$10,000 or more",
        "Unsure / prefer not to answer"
    ]
)

# GENERATE CARD

if st.button("Generate My Journey Card", type="primary"):

    symptoms = []

    if rash:
        symptoms.append("New or expanding rash")
    if fever:
        symptoms.append("Fever")
    if fatigue:
        symptoms.append("Fatigue")
    if headache:
        symptoms.append("Headache")
    if pain:
        symptoms.append("Muscle or joint pain")

    symptom_text = ", ".join(symptoms) if symptoms else "None reported"

    st.divider()
    st.header("My PathwayAI Journey Card")

    # Exposure

    st.subheader("Exposure Context")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Location", location)
        st.metric("Travel Month", month)

    with col2:
        st.metric("Age", age)
        st.metric("Tick Bite", tick_bite)

    st.write(f"**Attachment duration:** {attachment}")
    st.write(f"**Immune status:** {immune}")
    st.write(f"**Reported symptoms:** {symptom_text}")

    if location == "Dutchess County, New York":
        st.subheader("Local Environmental Surveillance")

        st.write(f"**NYSDOH surveillance year:** {int(latest_dutchess['Year'])}")
        st.write(f"**Nymph ticks collected:** {int(latest_dutchess['Total Ticks Collected'])}")
        st.write(f"**Nymph tick population density:** {latest_dutchess['Tick Population Density']}")
        st.write(f"**Nymphs tested:** {int(latest_dutchess['Total Tested'])}")
        st.write(f"**B. burgdorferi positive:** {latest_dutchess['B. burgdorferi (%)']}")

        st.caption(
        "Source: New York State Department of Health deer tick surveillance. "
        "These environmental surveillance data do not represent an individual's "
        "probability of Lyme disease."
    )



    # Navigation

    st.subheader("Navigation Priority")

    signals = []

    if tick_bite == "Yes":
        signals.append("reported tick exposure")

    if attachment == "Unsure":
        signals.append("unknown attachment duration")

    if rash:
        signals.append("new or expanding rash")

    if fever:
        signals.append("fever")

    if fatigue:
        signals.append("fatigue")

    if immune == "Yes":
        signals.append("relevant immune condition")

    if len(signals) >= 3:
        priority = "Higher navigation priority"
        explanation = (
            "Multiple exposure and symptom signals are present. "
            "These signals support timely clinical evaluation and careful documentation."
        )

    elif len(signals) >= 1:
        priority = "Moderate navigation priority"
        explanation = (
            "One or more exposure or symptom signals are present. "
            "Continue monitoring and document changes."
        )

    else:
        priority = "Routine prevention and monitoring"
        explanation = (
            "No major exposure or symptom signals were reported in this prototype."
        )

    st.warning(priority)
    st.write(explanation)

    st.subheader("Why PathwayAI Flagged This")

    if signals:
        for signal in signals:
            st.write(f"• {signal.capitalize()}")
    else:
        st.write("• No major signals reported")

    st.caption(
        "This is an explainable navigation rule for the beta prototype, "
        "not a validated Lyme disease prediction score."
    )

    # Functional impact

    st.subheader("Functional Impact & Disability")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Daily Activities", daily_function)

    with col2:
        st.metric("Days Missed", days_missed)

    st.write(f"**Work/school impact:** {work_impact}")

    if (
        daily_function in ["Major limitation", "Unable to perform usual activities"]
        or work_impact in ["Stopped working or school", "On disability"]
    ):
        st.info(
            "Significant functional impact reported. PathwayAI records this "
            "separately from clinical navigation priority."
        )

    # Patient journey and economic burden

    st.subheader("💰 My Burden Snapshot")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Healthcare Professionals Seen", providers_seen)

    with col2:
        st.metric("Days Missed", days_missed)

    st.write(f"**Time to diagnosis:** {diagnostic_delay}")
    st.write(f"**Out-of-pocket cost:** {oop_cost}")
    st.write(f"**Work/school impact:** {work_impact}")

    st.caption(
        "These measures document patient-reported healthcare utilization, "
        "functional impact, productivity loss, and direct out-of-pocket burden."
    )
        	
    # Journey summary

    st.subheader("The Invisible Patient Journey")

    st.write("**Possible Exposure**")
    st.write("↓")
    st.write("**Symptoms Begin**")
    st.write("↓")
    st.write(f"**Healthcare Journey — {providers_seen} healthcare professionals seen**")
    st.write("↓")
    st.write(f"**Diagnostic Journey — {diagnostic_delay}**")
    st.write("↓")
    st.write(f"**Functional Impact — {daily_function}**")
    st.write("↓")
    st.write(f"**Economic Burden — {oop_cost} out of pocket**")

    # Next steps

    st.subheader("Evidence-Grounded Next Steps")

    if tick_bite == "Yes":
        st.write(
            "• Record the date and geographic location of the possible tick exposure."
        )

    if attachment == "Unsure":
        st.write(
            "• If possible, document when the tick was first noticed and when it was removed."
        )

    if fever:
        st.write(
            "• Record when the fever began and whether other symptoms develop."
        )

    if symptoms:
        st.write(
            "• Bring your exposure and symptom timeline to an appropriate healthcare professional."
        )

    if daily_function != "No limitation" or work_impact != "No impact":
        st.write(
            "• Document changes in daily function and work/school participation over time."
        )

    st.write(
        "• Continue monitoring for new or changing symptoms after possible tick exposure."
    )

    # Provenance

    st.subheader("Data Sources & Provenance")

    provenance = pd.DataFrame(
        {
            "Information": [
                "Travel location",
                "Travel month",
                "Age / immune status",
                "Tick exposure",
                "Symptoms",
                "Functional impact",
                "Work/school impact",
                "Diagnostic journey",
                "Healthcare utilization",
                "Out-of-pocket cost",
                "Navigation output",
            ],
            "Source": [
                "User-reported + public geographic data",
                "User-reported + seasonal context",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "Prototype evidence-grounded rules",
            ],
            "Role in PathwayAI": [
                "Exposure context",
                "Seasonal context",
                "Personal context",
                "Exposure history",
                "Clinical context",
                "Functional burden",
                "Productivity impact",
                "Diagnostic delay",
                "Healthcare utilization",
                "Direct economic burden",
                "Explainable navigation",
            ],
        }
    )

    st.dataframe(
        provenance,
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "PathwayAI separates patient-reported information, public data, "
        "and prototype-derived outputs so users can see where each piece "
        "of information comes from."
    )

    st.error(
        "PathwayAI does not diagnose Lyme disease or prescribe treatment. "
        "Seek professional medical evaluation for concerning symptoms or "
        "illness after possible tick exposure."
    )