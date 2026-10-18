import unittest
from pathlib import Path
from support_summary import support_summary
from streamlit.testing.v1 import AppTest


class SupportSummaryTests(unittest.TestCase):
    def test_sensitive_fields_are_opt_in_and_need_specific(self):
        record = {"medical": 180, "workdays": 3, "period": "Past 30 days",
                  "story": "PRIVATE STORY", "daily_life_context": {
                      "person_daily_effects": ["Work or school"], "caregiver_own_experience": "PRIVATE CAREGIVER"}}
        basic = support_summary("Disability benefits", "Help", record)
        self.assertNotIn("Workdays missed", basic)
        text = support_summary("Disability benefits", "Help", record, True)
        self.assertNotIn("Workdays missed: 3", text)
        self.assertIn("Work or school", text)
        self.assertIn("do not establish disability eligibility", text)
        for private in ("180", "PRIVATE STORY", "PRIVATE CAREGIVER"):
            self.assertNotIn(private, text)
        food = support_summary("Food or housing", "Help", record, True)
        self.assertNotIn("Workdays missed", food)
        self.assertNotIn("Work or school", food)
        self.assertIn("MY REVIEWED DETAILS", support_summary("Paying for care", "Help", reviewed_story="MY REVIEWED DETAILS"))

    def test_support_choices_download_and_preserve_costs(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.number_input(key="medical88").set_value(180).run()
        for need in ("Food or housing", "Disability benefits", "Paying for care"):
            at.selectbox(key="support_need89").set_value(need).run()
            self.assertFalse(list(at.exception))
            self.assertEqual(at.number_input(key="medical88").value, 180)
            self.assertTrue(any(x.key == "support_summary_download" for x in at.get("download_button")))
        at.checkbox(key="support_summary_facts").check().run()
        self.assertIn("Money paid for care ($): 180", at.text_area(key="support_summary_text").value)
        at.text_input(key="bill_organization").set_value("Example Clinic").run()
        at.text_input(key="bill_date").set_value("July 2026, approximate").run()
        at.number_input(key="bill_balance").set_value(420).run()
        self.assertIn("Billing organization: Example Clinic", at.text_area(key="support_summary_text").value)
        self.assertIn("Balance stated on bill ($): 420", at.text_area(key="support_summary_text").value)
        self.assertEqual(at.number_input(key="medical88").value, 180)
        at.selectbox(key="support_need89").set_value("Food or housing").run()
        at.selectbox(key="support_need89").set_value("Paying for care").run()
        self.assertEqual(at.text_input(key="bill_organization").value, "Example Clinic")
        self.assertEqual(at.number_input(key="bill_balance").value, 420)
        at.text_area(key="support_summary_text").set_value("My edited request").run()
        self.assertEqual(at.text_area(key="support_summary_text").value, "My edited request")
