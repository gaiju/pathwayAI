import unittest
from pathlib import Path
from story_prefill import story_burden_defaults88, apply_story_burden_defaults88

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


class StoryPrefillTests(unittest.TestCase):
    def test_explicit_payments_and_decimal(self):
        for story, expected in [
            ("I paid $450 for medical bills and $80 for travel.", {"medical88": 450, "other88": 80}),
            ("I paid $1,250.50 for medical care and $80 for travel.", {"medical88": 1250.5, "other88": 80}),
            ("I paid $450 for medical bills. I also spent $120 on transport.", {"medical88": 450, "other88": 120}),
            ("I paid $450 for medical bills. My insurer paid the specialist bill.", {"medical88": 450}),
            ("I paid $0 for medical care.", {"medical88": 0}),
        ]:
            with self.subTest(story=story):
                self.assertEqual(story_burden_defaults88(story), (expected, {}))

    def test_uncertain_other_person_and_insurance_not_copied(self):
        for story in ["My medical bills were $500. My insurer paid everything.",
                      "I paid about $450 for medical bills.", "I didn't pay $450 for medical bills.",
                      "I never said I paid $450 for medical bills and $80 for travel.",
                      "My husband missed 5 workdays and another 3 workdays.",
                      "I was off work for three months.", "I missed 3651 workdays."]:
            with self.subTest(story=story):
                self.assertEqual(story_burden_defaults88(story), ({}, {}))

    def test_ambiguous_totals_need_review(self):
        for story, key in [("I paid $450 and another $200 for medical bills.", "medical88"),
                           ("I missed 5 workdays and another 3 workdays.", "workdays88")]:
            defaults, notes = story_burden_defaults88(story)
            self.assertNotIn(key, defaults)
            self.assertIn(key, notes)

    def test_rates_not_assumed_to_be_totals(self):
        self.assertEqual(story_burden_defaults88("I paid $450 for medical bills and $80 for travel per week."), ({"medical88": 450}, {}))

    def test_corrections_and_cleared_fields_survive_refresh(self):
        for correction in (None, 700):
            state = {}
            apply_story_burden_defaults88(state, {"medical88": 450})
            state["medical88"] = correction
            apply_story_burden_defaults88(state, {"medical88": 500})
            apply_story_burden_defaults88(state, {"medical88": 600})
            self.assertEqual(state["medical88"], correction)

    @unittest.skipIf(AppTest is None, "Streamlit is required")
    def test_app_review_correction_navigation_and_story_change(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.text_area(key="quick_story_value").set_value("I paid $120 for medical care. I missed 3 workdays.").run()
        next(x for x in at.button if x.label == "✨ Organize My Story").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.number_input(key="medical88").value, 120)
        self.assertEqual(at.number_input(key="workdays88").value, 3)
        self.assertTrue(any("From your story — please review" in x.value for x in at.markdown))
        at.number_input(key="medical88").set_value(150).run()
        at.button(key="patient_to_community").click().run()
        at.button(key="community_cost_record").click().run()
        self.assertEqual(at.number_input(key="medical88").value, 150)
        at.text_area(key="quick_story_value").set_value("I need help preparing for care.").run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.number_input(key="medical88").value, 150)
        self.assertIsNone(at.number_input(key="workdays88").value)
