"""Public care-access guidance; no eligibility decisions or patient-data collection."""
from report_download import branded_download_button

HRSA = "https://findahealthcenter.hrsa.gov/"
COVERAGE = "https://www.healthcare.gov/have-job-based-coverage/if-you-lose-job-based-coverage/"
NY_COVERAGE = "https://nystateofhealth.ny.gov/"
MEDICAL_DEBT = "https://www.consumerfinance.gov/consumer-tools/medical-debt/"
HOSPITAL_ASSISTANCE = "https://www.irs.gov/charities-non-profits/financial-assistance-policies-faps"
CDC_BITE = "https://www.cdc.gov/ticks/after-a-tick-bite/index.html"
CDC_TREATMENT = "https://www.cdc.gov/lyme/treatment/index.html"
LYME_SERVICE_EXAMPLE = "https://www.cornellscott.org/programs-and-services/infectious-diseases"
PRIMARY_CARE_LYME = "Early Lyme disease can often be evaluated and treated in primary care. Services vary by health center and location; a listing in the HRSA locator does not confirm Lyme-specific services or appointment availability."
HOOK_COST_STUDY = "https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article"
TIMELY_CARE_MESSAGE = "Early diagnosis and appropriate antibiotic treatment can help prevent more severe Lyme disease. If untreated, the infection can affect the joints, nerves or heart. A clinician decides what care you need."
EMERGENCY_REMINDER = "Get emergency help: Call 911 for chest pain, severe trouble breathing, or fainting. These can signal a serious problem, whether or not it is related to a tick bite. Do not delay because you lack insurance."


def care_access_questions():
    return "\n".join([
        "PathwayAI | Questions about uninsured care and medical bills",
        "Use these questions directly with a health center, enrollment assister or billing office.",
        "You do not need to share a patient story with PathwayAI to use this guide.",
        "", "SEEK TIMELY CARE",
        "Contact a clinician promptly about a new rash, fever or other symptoms after possible tick exposure. Tell them when and where it happened.",
        "Some high-risk tick bites may qualify for preventive antibiotics within 72 hours of tick removal. Ask promptly; antibiotics are not needed after every bite.",
        TIMELY_CARE_MESSAGE,
        "Do not wait for coverage paperwork before contacting a clinician. Ask about care and financial assistance together.",
        "", "CALL A COMMUNITY HEALTH CENTER",
        "I do not have insurance. Are you accepting new patients?",
        PRIMARY_CARE_LYME,
        "Can you evaluate a tick bite or possible Lyme disease, and how soon can I be seen?",
        "Do you provide Lyme testing and treatment when appropriate, or coordinate a specialist referral?",
        "Can you provide a qualified interpreter for the visit?",
        "How do I apply for your sliding-fee discount? Which income and household documents do you need?",
        "What would the visit cost? Are outside tests, medicines and referrals charged separately?",
        "Can an enrollment assister help me check coverage options?",
        "Health centers serve uninsured patients. Discounts depend on income and family size; care is not automatically free.",
        "", "ASK ABOUT COVERAGE",
        "I lost job-based coverage. Can I use a Special Enrollment Period or apply for Medicaid?",
        "What deadlines, eligibility rules and documents apply to my household?",
        "Clinic access and insurance eligibility are different. This guide does not determine either.",
        "", "CALL THE BILLING OFFICE",
        "Emergency care may still be billed. Ask the hospital about financial assistance; do not delay emergency care because of cost.",
        "Please send an itemized bill and explain any charges I do not understand.",
        "Can I apply for financial assistance or charity care? Please send the written policy and application.",
        "Does assistance cover each clinician, laboratory and other bill, or must I apply separately?",
        "Can you pause collection activity while you review my application? Please confirm any agreement in writing.",
        "If I still owe money, are self-pay discounts or an interest-free payment plan available?",
        "Before non-emergency self-pay care, how can I request a good faith estimate?",
        "Assistance, discounts and payment terms depend on the provider and your circumstances; none is guaranteed.",
        "", "OFFICIAL STARTING POINTS",
        "Health centers: " + HRSA,
        "Lost coverage: " + COVERAGE,
        "New York coverage assistance: " + NY_COVERAGE,
        "Medical bills: " + MEDICAL_DEBT,
        "Nonprofit hospital financial-assistance policies: " + HOSPITAL_ASSISTANCE,
        "After a tick bite: " + CDC_BITE,
        "Lyme treatment: " + CDC_TREATMENT,
        "", EMERGENCY_REMINDER,
        "PathwayAI helps you find resources and prepare questions. It does not enroll you, pay bills or arrange an appointment.",
    ])


def show_timely_care(navigate):
    import streamlit as st

    st.markdown("### Find care and prepare for your visit")
    st.write("Contact a clinician promptly about symptoms after possible tick exposure. Do not wait for insurance paperwork before asking about care.")
    st.write(TIMELY_CARE_MESSAGE)
    st.markdown(f"[CDC: treatment and recovery]({CDC_TREATMENT})")
    st.write("Recently bitten? See Tick Bite: What Next? for removal steps and time-sensitive advice.")
    st.button("Tick Bite: What Next? →", key="care_to_tick_bite", on_click=navigate,
              args=("🩹 Tick Bite: What Next?", "bite"))
    st.caption(EMERGENCY_REMINDER)


def show_lyme_cost_context():
    import streamlit as st

    with st.expander("Why early care matters: localized and disseminated Lyme", expanded=st.session_state.get("reading_mode") == "More detail"):
        st.write(TIMELY_CARE_MESSAGE)
        st.write("Localized Lyme refers to infection at the initial site. Disseminated Lyme has spread to other parts of the body and can require more complex care.")
        st.markdown(f"[CDC: treatment and recovery]({CDC_TREATMENT})")
        st.markdown("**What published cost research found**")
        st.table([
            {"Study group": "Confirmed localized Lyme", "Mean societal cost (2016 USD)": "$1,307"},
            {"Study group": "Confirmed disseminated Lyme", "Mean societal cost (2016 USD)": "$3,251"},
        ])
        st.caption("Hook et al. (2022): societal costs include medical, nonmedical and productivity costs. These are study-group averages, not a prediction of your bill. Do not add these averages to your own expenses.")
        st.write("The study compared disease groups. It did not show that each delayed diagnosis causes a particular extra cost, or that earlier care through PathwayAI saves $1,944. It did not measure long-term disability caused by delay.")
        st.markdown(f"[Read Hook et al. (2022): study methods and limits]({HOOK_COST_STUDY})")
        st.write("Practical next step: tell the clinician about exposure, symptoms, their timing and any test results. If cost or language makes care harder to reach, use the support resources on this page. PathwayAI helps with preparation; reduced delays or savings have not been established.")


def show_care_access(include_bills=True):
    import streamlit as st

    st.markdown("### No insurance or worried about medical bills?")
    st.write("Find care you can access. You can use these resources without entering a story, ZIP code or personal documents.")
    st.markdown(f"[Find a community health center — HRSA]({HRSA}). Health centers serve uninsured patients and offer sliding-fee discounts based on income and family size. Care is not automatically free.")
    st.write(PRIMARY_CARE_LYME)
    with st.expander("Can a health center help with Lyme disease?"):
        st.write("Ask whether the location evaluates tick bites or possible Lyme disease, offers testing and treatment when appropriate, or coordinates specialist referrals. Ask how soon you can be seen and whether interpreter services are available.")
        st.markdown(f"[CDC: Lyme treatment]({CDC_TREATMENT})")
        st.markdown(f"[Example: Cornell Scott–Hill Health Center infectious disease services, Connecticut]({LYME_SERVICE_EXAMPLE})")
        st.caption("Provider example supplied for reference; current services have not been independently confirmed by PathwayAI. This is not a verified Dutchess or Orange County referral. Confirm appointments, services and fees directly.")
    with st.expander("Care without insurance: what to ask"):
        st.write("Call the center about new-patient appointments, evaluation for a tick bite or possible Lyme disease, and sliding-fee assistance. Ask what the visit, outside tests, medicines and referrals would cost.")
        st.write("HRSA-funded health centers serve patients regardless of immigration status; you do not have to be a lawful resident to seek care there. Insurance programs have separate eligibility rules. Ask the center what documents it needs for fee assistance.")
    with st.expander("Lost insurance? Check coverage options"):
        st.markdown(f"[Losing job-based coverage: enrollment options — HealthCare.gov]({COVERAGE})")
        st.write("Losing job-based coverage may qualify you for a time-limited Special Enrollment Period. Medicaid applications are accepted year-round. An enrollment assister can explain deadlines, household and income rules, and any applicable immigration requirements.")
        st.markdown(f"[New York State of Health: coverage and enrollment assistance]({NY_COVERAGE})")
        st.caption("Coverage is not automatic. An assister or the relevant program must check your circumstances.")
    if include_bills:
        show_billing_help()


def show_billing_help():
    import streamlit as st

    with st.expander("Already have a high medical bill?"):
        st.write("Emergency care may still be billed. Ask the hospital about financial assistance; do not delay emergency care because of cost.")
        st.markdown("1. **Ask for an itemized bill.** Check unfamiliar, duplicate or incorrect charges with the billing office.\n2. **Ask about financial assistance or charity care.** Request the written policy, application and deadlines. Nonprofit hospitals must have a financial-assistance policy for emergency and other medically necessary hospital care; eligibility and covered providers vary. Ask separately about outside clinician and laboratory bills.\n3. **Ask about collections and payment options.** Ask whether collection activity can pause during review. If a balance remains, ask about self-pay discounts or an interest-free plan. Get agreements in writing.")
        st.write("Before scheduled non-emergency care, uninsured or self-pay patients can ask about a good faith estimate. A bill substantially above the estimate may qualify for a federal dispute process; check the current rules and deadlines.")
        st.markdown(f"[Medical-bill help — CFPB]({MEDICAL_DEBT}) · [Nonprofit hospital assistance policies — IRS]({HOSPITAL_ASSISTANCE})")
    branded_download_button("Download questions about uninsured care and bills", care_access_questions().encode("utf-8"),
                       file_name="PathwayAI_Uninsured_Care_and_Bills.txt", mime="text/plain", key="care_access_questions")
    st.caption("PathwayAI helps you find resources and prepare questions. It does not enroll you in coverage, pay bills or arrange appointments. Confirm fees, assistance and availability directly with each service.")


def show_transport_help(resource):
    """Reuse the app's existing county referral information without a story form."""
    import streamlit as st

    st.markdown("- **Anywhere in the U.S.:** Contact [211](https://www.211.org/) to ask about local transportation assistance.\n- **Have Medicaid?** Ask your plan or state Medicaid program about non-emergency medical transportation. [New York transportation information](https://www.health.ny.gov/health_care/medicaid/members/medtrans_overview.htm).\n- **In Dutchess County?** Older adults without Medicaid can call **845-486-2555** to ask about GoGo registration and availability. [Dutchess transportation information](https://www.dutchessny.gov/Departments/Aging/Transportation-for-Seniors.htm).")
    st.write("Before booking, ask: Am I eligible? Is registration required? What does it cost? How early must I book? Is an accessible vehicle available? Is the return trip included?")
    st.caption("Confirm eligibility, availability and costs with the service. PathwayAI does not arrange or pay for rides. These resources are for non-emergency appointments.")
