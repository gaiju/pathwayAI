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
