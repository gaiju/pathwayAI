import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from caregiver_record import REPORTERS, reporting_lines

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

APP = Path(__file__).resolve().parents[1] / "app.py"


class CaregiverRecordTests(unittest.TestCase):
    def test_sources_and_experiences_are_separate(self):
        lines = reporting_lines(REPORTERS[2], {
            "person_daily_effects": ["Speaking or communicating"],
            "caregiver_own_experience": "I missed family events.",
        })
        text = "\n".join(lines)
        self.assertIn("Caregiver observations", text)
        self.assertIn("DAILY-LIFE EFFECTS FOR THE PERSON RECEIVING CARE", text)
        self.assertIn("CAREGIVER'S OWN EXPERIENCE", text)
        self.assertLess(lines.index("DAILY-LIFE EFFECTS FOR THE PERSON RECEIVING CARE"), lines.index("CAREGIVER'S OWN EXPERIENCE"))

    def test_proxy_cannot_write_into_existing_patient_aggregation(self):
        tree = ast.parse(APP.read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "save_voice88")
        scope = {"PATIENT_VOICE_STORAGE_ENABLED": True, "REPORTERS": REPORTERS,
                 "st": SimpleNamespace(session_state={"reporter_role": REPORTERS[2]})}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(APP), "exec"), scope)
        self.assertFalse(scope["save_voice88"]({}))

    @unittest.skipIf(AppTest is None, "Streamlit is required")
    def test_proxy_details_download_and_navigation(self):
        at = AppTest.from_file(str(APP), default_timeout=60).run()
        at.button(key="route_ongoing").click().run()
        at.selectbox(key="reporter_role").set_value(REPORTERS[2]).run()
        at.text_area(key="quick_story_value").set_value("I paid $120 for medical care. My relative needs help preparing for care.").run()
        next(b for b in at.button if b.label == "✨ Organize My Story").click().run()
        self.assertFalse(list(at.exception))
        self.assertIsNone(at.number_input(key="medical88").value)
        at.multiselect(key="person_daily_effects").set_value(["Speaking or communicating"]).run()
        at.text_area(key="caregiver_own_experience").set_value("I missed an important family event.").run()
        summary = at.text_area(key="summary88_text").value
        self.assertIn("Caregiver observations", summary)
        self.assertIn("Speaking or communicating", summary)
        self.assertIn("CAREGIVER'S OWN EXPERIENCE", summary)
        self.assertIn("I missed an important family event.", summary)
        self.assertFalse(at.checkbox(key="use_story_ai65").value)
        at.button(key="patient_to_community").click().run()
        at.button(key="community_cost_record").click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.selectbox(key="reporter_role").value, REPORTERS[2])
        self.assertEqual(at.text_area(key="caregiver_own_experience").value, "I missed an important family event.")
