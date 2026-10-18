import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit is required for story workflow checks")
class StoryGuidanceTests(unittest.TestCase):
    def test_summary_is_immediate_editable_and_not_marked_current_after_story_changes(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        at = AppTest.from_file(str(app), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        story = "I walked in Virginia in May. I felt tired for ten days. I paid $180 for medical care."
        at.text_area(key="quick_story_value").set_value(story).run()
        next(b for b in at.button if "Organize My Story" in b.label).click().run()
        self.assertFalse(list(at.exception))
        self.assertIn(story, at.text_area(key="visit_summary_edit").value)
        self.assertTrue(any(d.label == "Download my visit summary" for d in at.get("download_button")))
        content = "\n".join(str(x.value) for x in at.markdown)
        self.assertLess(content.index("Your organized visit summary"), content.index("Your costs, time and visit summary"))
        corrected = at.text_area(key="visit_summary_edit").value + "\nMy question: what follow-up is appropriate?"
        at.text_area(key="visit_summary_edit").set_value(corrected).run()
        at.number_input(key="medical88").set_value(200).run()
        self.assertEqual(at.text_area(key="visit_summary_edit").value, corrected)
        at.text_area(key="quick_story_value").set_value("I have a different question for my visit.").run()
        self.assertFalse(any(x.value == "Your visit summary is ready to review." for x in at.success))
        self.assertFalse(any(x.key == "visit_summary_edit" for x in at.text_area))

    def test_example_is_read_only_and_personal_story_survives_navigation(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        at = AppTest.from_file(str(app), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.text_area(key="quick_story_value").value, "")
        self.assertFalse(at.checkbox(key="use_story_ai65").value)
        self.assertFalse(any(button.label == "Try this example" for button in at.button))
        self.assertTrue(any(expander.label == "Read a made-up example" for expander in at.expander))
        self.assertTrue(any("What symptoms have you had" in element.value for element in at.markdown))
        story = "I walked in Virginia in May. I have felt tired for ten days. I need help preparing for a visit."
        at.text_area(key="quick_story_value").set_value(story).run()
        at.button(key="patient_to_community").click().run()
        at.button(key="community_cost_record").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.text_area(key="quick_story_value").value, story)
