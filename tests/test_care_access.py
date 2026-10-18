"""Check that uninsured visitors receive actionable help without giving a story."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from care_access import care_access_questions, HRSA, MEDICAL_DEBT, EMERGENCY_REMINDER
from community_action import action_brief


class CareAccessTests(unittest.TestCase):
    def test_uninsured_help_is_available_before_story_entry(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        self.assertTrue(any("A working pilot web app for people affected by Lyme disease" in x.value for x in at.markdown))
        self.assertFalse(any(x.label == "Reviewer walkthrough · 90 seconds" for x in at.expander))
        at.button(key="route_ongoing").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.text_area(key="quick_story_value").value, "")
        self.assertFalse(any(x.value for x in at.text_input if "ZIP" in x.label or "location" in x.label.lower()))
        content = "\n".join(str(x.value) for x in at.markdown)
        self.assertLess(content.index("Find care and prepare for your visit"), content.index("No insurance or worried about medical bills?"))
        self.assertLess(content.index("No insurance or worried about medical bills?"), content.index("Tell us what happened"))
        self.assertNotIn("72 hours of tick removal", content)
        self.assertIn("not a prediction of your bill", content)
        self.assertIn(HRSA, content)
        self.assertIn(MEDICAL_DEBT, content)
        self.assertIn("Care is not automatically free", content)
        self.assertIn("regardless of immigration status", content)
        self.assertIn("845-486-2555", content)
        self.assertIn("does not book or fund rides", "\n".join(str(x.value) for x in at.caption))
        self.assertTrue(any(d.label == "Download questions about uninsured care and bills" for d in at.get("download_button")))

    def test_cross_page_links_preserve_patient_entries_and_bite_guidance(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.text_area(key="quick_story_value").set_value("I need help preparing for a visit.").run()
        at.number_input(key="medical88").set_value(125).run()
        at.button(key="care_to_tick_bite").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.radio(key="pathway_view").value, "🩹 Tick Bite: What Next?")
        self.assertTrue(any("within 72 hours of tick removal" in x.value for x in at.markdown))
        at.button(key="bite118_to_care").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.radio(key="pathway_view").value, "🧭 Care & Support")
        self.assertEqual(at.text_area(key="quick_story_value").value, "I need help preparing for a visit.")
        self.assertEqual(at.number_input(key="medical88").value, 125)

    def test_takeaway_and_community_brief_include_real_next_steps_and_limits(self):
        questions = care_access_questions()
        self.assertIn("whether or not it is related to a tick bite", EMERGENCY_REMINDER)
        self.assertNotIn("billed", EMERGENCY_REMINDER)
        self.assertIn("Emergency care may still be billed", questions)
        for phrase in ("sliding-fee", "itemized bill", "written policy", "charged separately", "Special Enrollment Period", "none is guaranteed"):
            self.assertIn(phrase, questions)
        brief = action_brief("Care without insurance and medical bills")
        self.assertIn("possible funding source", brief)
        self.assertIn("record the need as unmet", brief)
        self.assertIn("does not secure funding", brief)
        self.assertIn("not all county residents", brief)
