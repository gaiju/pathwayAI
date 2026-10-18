"""Check that uninsured visitors receive actionable help without giving a story."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from care_access import care_access_questions, HRSA, MEDICAL_DEBT
from community_action import action_brief


class CareAccessTests(unittest.TestCase):
    def test_uninsured_help_is_available_before_story_entry(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.text_area(key="quick_story_value").value, "")
        self.assertFalse(any(x.value for x in at.text_input if "ZIP" in x.label or "location" in x.label.lower()))
        content = "\n".join(str(x.value) for x in at.markdown)
        self.assertLess(content.index("Get timely care"), content.index("No insurance or worried about medical bills?"))
        self.assertLess(content.index("No insurance or worried about medical bills?"), content.index("Tell us what happened"))
        self.assertIn("72 hours of tick removal", content)
        self.assertIn("antibiotics are not needed after every bite", content)
        self.assertIn("not a prediction of your bill", content)
        self.assertIn(HRSA, content)
        self.assertIn(MEDICAL_DEBT, content)
        self.assertIn("Care is not automatically free", content)
        self.assertIn("regardless of immigration status", content)
        self.assertTrue(any(d.label == "Download questions about uninsured care and bills" for d in at.get("download_button")))

    def test_takeaway_and_community_brief_include_real_next_steps_and_limits(self):
        questions = care_access_questions()
        for phrase in ("sliding-fee", "itemized bill", "written policy", "charged separately", "Special Enrollment Period", "none is guaranteed"):
            self.assertIn(phrase, questions)
        brief = action_brief("Care without insurance and medical bills")
        self.assertIn("possible funding source", brief)
        self.assertIn("record the need as unmet", brief)
        self.assertIn("does not secure funding", brief)
        self.assertIn("not all county residents", brief)
