import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class CommunityShortcutTests(unittest.TestCase):
    def test_pathway_shortcuts_and_sample_are_reachable(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_county").click().run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any("Orange" in item.value for item in at.text))
        sample = next(d for d in at.get("download_button") if d.label == "Download sample Orange County brief (PDF)")
        self.assertIn(".pdf", sample.proto.url)
        if any(b.key == "community_step_0" for b in at.button):
            for index, expected_tab in enumerate((1, 2, 2, 3)):
                at.button(key="community_step_" + str(index)).click().run()
                self.assertFalse(list(at.exception))
                containers = [node.proto.tab_container for node in at.main
                              if getattr(node, "proto", None) is not None
                              and "tab_container" in node.proto.DESCRIPTOR.fields_by_name
                              and node.proto.HasField("tab_container")]
                self.assertEqual(containers[0].default_tab_index, expected_tab)
            self.assertTrue(next(e for e in at.expander if e.label == "Local review checklist").proto.expanded)
        for index, target in enumerate(("🛡️ Learn & Prevent", "🧭 Care & Support", "🧭 Care & Support", "🧭 Care & Support")):
            at.button(key="community_patient_" + str(index)).click().run()
            self.assertFalse(list(at.exception))
            self.assertEqual(at.radio(key="pathway_view").value, target)
            at.radio(key="pathway_view").set_value("📊 Community Burden & Action").run()

