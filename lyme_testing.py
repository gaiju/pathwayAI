"""Public educational content only; no report upload, diagnosis or secret access."""

CDC_TESTING_URL = "https://www.cdc.gov/lyme/hcp/diagnosis-testing/index.html"
CDC_ABOUT_URL = "https://www.cdc.gov/lyme/diagnosis-testing/index.html"

PREPARATION_CHECKLIST = """PathwayAI | Questions before Lyme testing
Education and visit preparation, not a diagnosis or test interpretation.

BRING
- The original full lab report, including the final interpretation and comments.
- Dates of possible exposure, symptom onset and previous blood draws.
- A medication list, including any antibiotics and when you took them.
- Dated photos of a changing skin mark, if available.

ASK YOUR CLINICIAN
- Does my history call for testing, examination or another evaluation?
- Was the recommended two-step testing process completed?
- Was the timing of this blood draw suitable for the symptoms being evaluated?
- Does this result answer the current concern, or what follow-up is appropriate?
- Is any fasting or other preparation needed for the tests ordered?

ASK THE LAB AND INSURER
- What exact tests are ordered, and is a second test automatically added?
- Is the lab in network, and what is my estimated out-of-pocket payment?
- Are the blood draw, second test and office visit included or billed separately?
- What is the total self-pay price, and can I get a written estimate?

READING THE REPORT
- Use the laboratory's overall interpretation, not an isolated antibody band.
- Present or absent means detected or not detected for that row, not a diagnosis.
- Test timing, the full testing process and clinical findings matter.
- Antibodies may persist after treatment; antibody tests do not prove cure.

COST RECORD
If you pay for testing, include it once within money paid for care for the
same reporting period. Do not add a quoted estimate to money actually paid.

CDC testing guidance:
""" + CDC_TESTING_URL + "\n"


def show_lyme_testing(simple=True):
    import streamlit as st

    with st.expander("Lyme tests: prepare, ask about cost, understand the words"):
        st.write('**Start with your clinician.** A blood test is one part of the picture. Your symptoms, exposure and timing matter too.')
        st.write('If something seems attached to your skin, have it examined. Do the same for a lasting or changing skin mark. Ticks usually feed for days, not months. An old blood test may not explain a new concern.')
        st.write("Seek urgent care for severe symptoms such as fainting, trouble breathing "
                 "or chest pain. This page does not diagnose or recommend treatment.")
        prepare, cost, read = st.tabs(["Before the test", "Ask about cost", "Read the words"])
        with prepare:
            st.markdown("**Bring these to your visit:**\n"
                        "- Your full lab report, including comments.\n"
                        "- Dates of the bite or possible exposure, symptoms and blood draws.\n"
                        "- Your medication list and any antibiotics you have taken.\n"
                        "- Dated photos of a changing skin mark, if you have them.")
            st.write("Ask: ‘What can this test tell us? Was it taken at the right time? "
                     "What should I do if symptoms continue?’")
            st.write('You usually do not need to fast for a Lyme antibody test alone. Follow the lab or clinician’s instructions. Other tests may need preparation. Do not stop medicines on your own.')
        with cost:
            st.write('**There is no single price.** Ask for a written estimate. Your cost depends on the lab, the tests and your insurance. Ask how your deductible affects the bill.')
            st.write("Before the blood draw, ask the lab and insurer for a written estimate:")
            st.markdown("- Is this lab covered by my plan?\n"
                        "- Does the quote include the blood draw and any second test?\n"
                        "- Is the office visit a separate charge?\n"
                        "- What would I pay with insurance, or as a self-pay patient?")
            st.write('Record what you paid under **Money you paid for care**. Count it once. A price quote is not a payment. PathwayAI does not provide live lab prices or calculate insurance benefits.')
        with read:
            st.markdown("#### Practice with a fictional report")
            st.write("**Invented learning example — not the uploaded patient report or a diagnosis.**")
            st.write("Fictional patient: **John Smith** · Fictional date of birth: **January 1, 1980**")
            st.table([
                {"Report item": "Overall interpretation", "Example result": "Negative"},
                {"Report item": "An individual antibody band", "Example result": "Present"},
                {"Report item": "Other antibody bands", "Example result": "Absent"},
                {"Report item": "Laboratory comment", "Example result": "See the full testing process and clinical history"},
            ])
            st.write('**Read the overall result first.** One row says “Present.” The final result says “Negative.” That row alone does not make the test positive. This short example is not enough to check the lab’s criteria.')
            st.write("**Look at the overall result first.** ‘Present’ on one antibody band "
                     "does not by itself mean that the overall test is positive.")
            st.markdown("- **Negative:** the completed test did not meet its positive criteria. "
                        "Timing and the full clinical assessment still matter.\n"
                        "- **Positive:** the test met its criteria; your clinician interprets "
                        "it with your history. It does not by itself prove a current infection.\n"
                        "- **Equivocal:** an unclear result; ask whether the next testing step "
                        "or other follow-up is needed.\n"
                        "- **IgM and IgG:** types of antibodies, not stages of disease.\n"
                        "- **Present / absent:** detected / not detected on that row.")
            st.write('A test can be negative early, before antibodies develop. Antibodies can remain after treatment. An antibody test does not show whether someone is cured.')
            st.write("Ask: ‘Was the full recommended testing process done, and how does "
                     "this result fit my symptoms and their timing?’")
            st.markdown("#### Prepare for the next conversation")
            st.markdown("1. Bring the complete original report, including lab comments.\n"
                        "2. Note when symptoms started, when the blood was drawn and any antibiotics taken.\n"
                        "3. Ask what the result means for your current concern and what follow-up is appropriate.")
            st.write('One “Present” row is not a reason to change treatment or order another test on your own. Ask your clinician what needs checking next.')
            if not simple:
                st.write("CDC recommends a two-step antibody testing process using "
                         "FDA-cleared tests. A positive or equivocal first step proceeds to "
                         "the second. Some processes use an immunoblot (Western blot); others "
                         "use a second enzyme immunoassay. Individual bands should not be "
                         "counted as a separate diagnosis.")
                st.write("CDC says positive IgM results should be disregarded when illness "
                         "has lasted more than 30 days. Ask the clinician to interpret the "
                         "appropriate results and the complete testing history.")
        st.download_button("Download Lyme testing questions", PREPARATION_CHECKLIST.encode("utf-8"),
                           file_name="PathwayAI_LymeTestingQuestions.txt", mime="text/plain",
                           key="lyme_testing_questions")
        st.markdown(f"[CDC: clinical testing guidance]({CDC_TESTING_URL})")
        st.write("Education only. No patient report is uploaded, stored or sent to AI by this section.")
