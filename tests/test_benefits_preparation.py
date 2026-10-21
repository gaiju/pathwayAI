from pathlib import Path
import unittest
from benefits_preparation import preparation_checklist
from evidence_scope import EVIDENCE_SCOPE

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


class BenefitsPreparationTests(unittest.TestCase):
    def test_disability_checklist_reuses_only_selected_facts(self):
        record = {"workdays": 3, "caregiver_hours": 8, "reported_by": "Myself",
                  "period": "Past 30 days", "story": "PRIVATE STORY", "medical": 180}
        text = preparation_checklist("SSDI", record)
        self.assertNotIn("Recorded workdays missed: 3", text)
        self.assertIn("at least 12 months", text)
        self.assertNotIn("Recorded unpaid help (hours): 8", text)
        self.assertNotIn("PRIVATE STORY", text)
        self.assertNotIn("180", text)
        self.assertIn("not an application", text)

    def test_tick_related_preparation_is_opt_in_and_does_not_infer_eligibility(self):
        base = preparation_checklist("SSDI")
        self.assertNotIn("IF YOU ARE PREPARING BECAUSE OF LYME", base)
        selected = preparation_checklist("SSDI", {"tick_related_preparation": True})
        self.assertIn("IF YOU ARE PREPARING BECAUSE OF LYME", selected)
        self.assertIn("A Lyme diagnosis alone does not establish eligibility", selected)
        self.assertIn("where you work", selected)
        self.assertIn("https://www.ssa.gov/forms/", selected)
        self.assertNotIn("IF YOU ARE PREPARING BECAUSE OF LYME", preparation_checklist("SNAP / food assistance", {"tick_related_preparation": True}))

    def test_snap_does_not_automatically_include_health_record(self):
        text = preparation_checklist("SNAP / food assistance", {"workdays": 3, "caregiver_hours": 8, "period": "Past 30 days"})
        self.assertNotIn("Recorded workdays", text)
        self.assertNotIn("Recorded unpaid help", text)
        self.assertIn("state-directory", text)

    def test_unknown_program_is_rejected(self):
        with self.assertRaises(ValueError):
            preparation_checklist("Invented program")

    def test_evidence_scopes_keep_denominators_and_limits(self):
        text = " ".join(str(row) for row in EVIDENCE_SCOPE)
        for item in ("613", "901", "466", "253", "missing answers", "Early-care cohort", "Not county prevalence"):
            self.assertIn(item, text)

    @unittest.skipIf(AppTest is None, "Streamlit is required")
    def test_checklist_and_source_scope_pages_work(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.number_input(key="workdays88").set_value(3).run()
        at.selectbox(key="benefits_program").set_value("SSDI").run()
        self.assertFalse(list(at.exception))
        self.assertFalse(any("Recorded workdays missed: 3" in x.value for x in at.text))
        self.assertTrue(any("at least 12 months" in x.value for x in at.text))
        self.assertTrue(any(x.key == "benefits_checklist_download" for x in at.get("download_button")))
        at.sidebar.radio(key="pathway_view").set_value("📚 Sources & Acknowledgements").run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any("Who and what the evidence covers" in x.value for x in at.markdown))
