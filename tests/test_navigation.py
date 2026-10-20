"""Regression checks for choosing a section from the welcome page."""
import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit is required for navigation checks")
class NavigationTests(unittest.TestCase):
    def test_community_opens_on_first_click_and_after_return(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        at = AppTest.from_file(str(app), default_timeout=60).run()
        self.assertIsNone(at.radio(key="pathway_view").value)
        for _ in range(2):
            at.radio(key="pathway_view").set_value("📊 Community Burden & Action").run()
            self.assertFalse(list(at.exception))
            self.assertTrue(any("Healthier people. Stronger communities." in e.value
                                for e in at.get("header")))
            at.button(key="change_path").click().run()
            self.assertIsNone(at.radio(key="pathway_view").value)
        at.button(key="route_county").click().run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any("Healthier people. Stronger communities." in e.value
                            for e in at.get("header")))

    def test_bite_notes_return_through_home_with_restored_widget_default(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        at = AppTest.from_file(str(app), default_timeout=60).run()
        at.button(key="route_bite").click().run()
        story = "Mixed 中文 notes: a tick in Pasadena, CA."
        at.text_area(key="quick_story_value").set_value(story).run()
        at.button(key="bite118_back").click().run()
        at.button(key="route_ongoing").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.text_area(key="quick_story_value").value, story)
        self.assertEqual(at.text_area(key="quick_story_value").proto.default, story)
        self.assertTrue(any("Your saved visit note" in e.value for e in at.markdown))
        # Chinese entered in English mode keeps edit controls open to resolve the mismatch.
        self.assertTrue(next(e for e in at.expander if e.label == "Review or edit your saved visit note").proto.expanded)
        at.text_area(key="quick_story_value").set_value("").run()
        at.button(key="change_path").click().run()
        at.button(key="route_bite").click().run()
        self.assertEqual(at.text_area(key="quick_story_value").value, "")

    def test_reused_english_note_collapses_questions_but_keeps_summary_visible(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_bite").click().run()
        story = "I found a tick in June. Two weeks later I had a rash. My blood test was negative."
        at.text_area(key="quick_story_value").set_value(story).run()
        next(b for b in at.button if "Organize My Story" in b.label).click().run()
        at.button(key="bite_continue_with_notes").click().run()
        self.assertFalse(list(at.exception))
        self.assertFalse(next(e for e in at.expander if e.label == "Review or edit your saved visit note").proto.expanded)
        self.assertEqual(at.text_area(key="quick_story_value").value, story)
        self.assertTrue(any(d.label == "Download my visit summary" for d in at.get("download_button")))
        self.assertIn("negative", at.text_area(key="visit_summary_edit").value)
        at.radio(key="reading_mode").set_value("More detail").run()
        self.assertTrue(next(e for e in at.expander if e.label == "Review or edit your saved visit note").proto.expanded)
        self.assertEqual(at.text_area(key="quick_story_value").value, story)
