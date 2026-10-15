import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit is required for story workflow checks")
class StoryGuidanceTests(unittest.TestCase):
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
