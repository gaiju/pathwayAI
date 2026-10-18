"""Public care-access guidance; no eligibility decisions or patient-data collection."""

HRSA = "https://findahealthcenter.hrsa.gov/"
COVERAGE = "https://www.healthcare.gov/have-job-based-coverage/if-you-lose-job-based-coverage/"
NY_COVERAGE = "https://nystateofhealth.ny.gov/"
MEDICAL_DEBT = "https://www.consumerfinance.gov/consumer-tools/medical-debt/"
HOSPITAL_ASSISTANCE = "https://www.irs.gov/charities-non-profits/financial-assistance-policies-faps"


def care_access_questions():
    return "\n".join([
        "PathwayAI | Questions about uninsured care and medical bills",
        "Use these questions directly with a health center, enrollment assister or billing office.",
        "You do not need to share a patient story with PathwayAI to use this guide.",
        "", "CALL A COMMUNITY HEALTH CENTER",
        "I do not have insurance. Are you accepting new patients?",
        "Can you evaluate a tick bite or possible Lyme disease, and how soon can I be seen?",
        "How do I apply for your sliding-fee discount? Which income and household documents do you need?",
        "What would the visit cost? Are outside tests, medicines and referrals charged separately?",
        "Can an enrollment assister help me check coverage options?",
        "Health centers serve uninsured patients. Discounts depend on income and family size; care is not automatically free.",
        "", "ASK ABOUT COVERAGE",
        "I lost job-based coverage. Can I use a Special Enrollment Period or apply for Medicaid?",
        "What deadlines, eligibility rules and documents apply to my household?",
        "Clinic access and insurance eligibility are different. This guide does not determine either.",
        "", "CALL THE BILLING OFFICE",
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
        "", "For an emergency, call 911 or go to an emergency department. Do not delay because you lack insurance; emergency care may still be billed.",
        "PathwayAI helps you find resources and prepare questions. It does not enroll you, pay bills or arrange an appointment.",
    ])


def show_care_access():
    import streamlit as st

    st.markdown("### No insurance or worried about medical bills?")
    st.write("Start here. You can use these resources without entering a story, ZIP code or personal documents.")
    st.markdown(f"**Need care now?** [Find a community health center — HRSA]({HRSA}). Health centers serve uninsured patients and offer sliding-fee discounts based on income and family size. Care is not automatically free.")
    with st.expander("Care without insurance: what to ask"):
        st.write("Call the center about new-patient appointments, evaluation for a tick bite or possible Lyme disease, and sliding-fee assistance. Ask what the visit, outside tests, medicines and referrals would cost.")
        st.write("HRSA-funded health centers serve patients regardless of immigration status; you do not have to be a lawful resident to seek care there. Insurance programs have separate eligibility rules. Ask the center what documents it needs for fee assistance.")
        st.write("If you need prompt advice after a tick bite or your symptoms are worsening, contact a clinician promptly rather than waiting for coverage paperwork.")
        st.caption("For an emergency, call 911 or go to an emergency department. Do not delay because you lack insurance; emergency care may still be billed.")
    with st.expander("Lost insurance? Check coverage options"):
        st.markdown(f"[Losing job-based coverage: enrollment options — HealthCare.gov]({COVERAGE})")
        st.write("Losing job-based coverage may qualify you for a time-limited Special Enrollment Period. Medicaid applications are accepted year-round. An enrollment assister can explain deadlines, household and income rules, and any applicable immigration requirements.")
        st.markdown(f"[New York State of Health: coverage and enrollment assistance]({NY_COVERAGE})")
        st.caption("Coverage is not automatic. An assister or the relevant program must check your circumstances.")
    with st.expander("Already have a high medical bill?"):
        st.markdown("1. **Ask for an itemized bill.** Check unfamiliar, duplicate or incorrect charges with the billing office.\n2. **Ask about financial assistance or charity care.** Request the written policy, application and deadlines. Nonprofit hospitals must have a financial-assistance policy for emergency and other medically necessary hospital care; eligibility and covered providers vary. Ask separately about outside clinician and laboratory bills.\n3. **Ask about collections and payment options.** Ask whether collection activity can pause during review. If a balance remains, ask about self-pay discounts or an interest-free plan. Get agreements in writing.")
        st.write("Before scheduled non-emergency care, uninsured or self-pay patients can ask about a good faith estimate. A bill substantially above the estimate may qualify for a federal dispute process; check the current rules and deadlines.")
        st.markdown(f"[Medical-bill help — CFPB]({MEDICAL_DEBT}) · [Nonprofit hospital assistance policies — IRS]({HOSPITAL_ASSISTANCE})")
    st.download_button("Download questions about uninsured care and bills", care_access_questions().encode("utf-8"),
                       file_name="PathwayAI_Uninsured_Care_and_Bills.txt", mime="text/plain", key="care_access_questions")
    st.caption("PathwayAI helps you find resources and prepare questions. It does not enroll you in coverage, pay bills or arrange appointments. Confirm fees, assistance and availability directly with each service.")
