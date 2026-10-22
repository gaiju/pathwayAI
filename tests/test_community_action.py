import unittest
from pathlib import Path

from community_action import ACTION_OPTIONS, action_brief, scenario_cost, pathway_evidence
from streamlit.testing.v1 import AppTest


class CommunityActionTests(unittest.TestCase):
    def test_export_preserves_source_period_type_and_limits(self):
        evidence = pathway_evidence()
        self.assertEqual(len(evidence), 4)
        for row in evidence:
            for key in ("Source", "Period", "Type", "Scope", "Reference"):
                self.assertTrue(row[key])
                self.assertIn(row[key], action_brief("Getting to care"))
        self.assertEqual(evidence[2]["Type"], "Synthetic demonstration")
        self.assertEqual(evidence[3]["Type"], "Assumption-based calculation")

    def test_brief_keeps_fictional_counts_separate_from_selected_priorities(self):
        for theme, plan in ACTION_OPTIONS.items():
            with self.subTest(theme=theme):
                brief = action_brief(theme)
                self.assertIn(plan["action"], brief)
                self.assertIn(plan["measure"], brief)
                self.assertIn("Six invented Dutchess-residence cards", brief)
                self.assertIn("Transportation / distance: 5 examples", brief)
                self.assertIn("one missing", brief)
                self.assertIn("does not create reports for that theme", brief)
                self.assertIn("not all county residents", brief)
                self.assertNotIn("EXAMPLE-1", brief)

    def test_scenario_recomputes_from_explicit_assumptions_including_zero(self):
        self.assertEqual(scenario_cost(3, 15), 45)
        self.assertEqual(scenario_cost(4, 12.5), 50)
        self.assertEqual(scenario_cost(0, 12.5), 0)

    def test_community_controls_and_combined_download_render(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.radio(key="pathway_view").set_value("📊 Community Burden & Action").run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any("Community Planning Templates" in item.value for item in at.markdown))
        at.selectbox(key="community_action_need").set_value("Food, housing and benefits").run()
        self.assertTrue(any("assisted applications" in item.value for item in at.markdown))
        at.number_input(key="action_trips").set_value(4).run()
        at.number_input(key="action_trip_cost").set_value(12.5).run()
        self.assertFalse(list(at.exception))
        metric = next(m for m in at.metric if m.label == "Illustrative travel spending for one person")
        self.assertEqual(metric.value, "$50.00")
        downloads = {d.label for d in at.get("download_button")}
        self.assertTrue(any("What you can do here" in item.value for item in at.markdown))
        self.assertIn("Download sourced planning template", downloads)
        self.assertEqual([tab.label for tab in at.tabs[:4]], ["Overview", "Plan community support", "Evidence & methods", "For residents"])


if __name__ == "__main__":
    unittest.main()
