import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit is required")
class ReadingModeTests(unittest.TestCase):
    def test_landing_mode_changes_route_explanations_and_preserves_all_choices(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        keys = ("route_bite", "route_ongoing", "route_outdoors", "route_county", "route_feedback")
        self.assertTrue(all(at.button(key=key) for key in keys))
        self.assertFalse(any("**You’ll get:**" in str(x.value) for x in at.markdown))
        at.radio(key="reading_mode").set_value("More detail").run()
        self.assertFalse(list(at.exception))
        self.assertEqual(sum("**You’ll get:**" in str(x.value) for x in at.markdown), 5)
        self.assertTrue(any("Review sources and assumptions" in str(x.value) for x in at.markdown))
        self.assertTrue(all(at.button(key=key) for key in keys))
        at.radio(key="reading_mode").set_value("Short and simple").run()
        self.assertFalse(list(at.exception))
        self.assertFalse(any("**You’ll get:**" in str(x.value) for x in at.markdown))
        self.assertTrue(all(at.button(key=key) for key in keys))

    def test_details_open_and_patient_entries_survive_switch(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.number_input(key="medical88").set_value(120).run()
        label = "See where costs arise in the care journey"
        self.assertFalse(next(x for x in at.expander if x.label == label).proto.expanded)
        at.radio(key="reading_mode").set_value("More detail").run()
        self.assertFalse(list(at.exception))
        self.assertTrue(next(x for x in at.expander if x.label == label).proto.expanded)
        self.assertEqual(at.number_input(key="medical88").value, 120)
        at.button(key="patient_to_community").click().run()
        self.assertEqual([tab.label for tab in at.tabs[:5]], ["Overview", "U.S. burden", "Plan community support", "Evidence & methods", "For residents"])
        label = "Exploratory survey comparisons · pending verification"
        self.assertFalse(next(x for x in at.expander if x.label == label).proto.expanded)
        at.radio(key="reading_mode").set_value("Short and simple").run()
        self.assertFalse(list(at.exception))
        self.assertFalse(next(x for x in at.expander if x.label == label).proto.expanded)
        at.button(key="community_cost_record").click().run()
        self.assertEqual(at.number_input(key="medical88").value, 120)
