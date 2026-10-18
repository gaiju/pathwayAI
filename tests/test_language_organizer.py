import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from language_organizer import translate_notes, validate_translation, bilingual_text, FIELDS
from visit_summary import visit_summary_text, story_details


def translated():
    return {"english_translation": "I found a tick in July. Two weeks later I had a rash and fever. My blood test was positive.",
            "timeline": {key: {"tick": "Patient reports finding a tick in July.", "onset": "Two weeks later.",
                               "rash": "Patient reports a rash.", "tests": "Patient reports a positive blood test; type/date not stated."}.get(key) for key in FIELDS},
            "uncertainties": ["Which blood test and date? Does four months refer to symptoms or diagnosis delay?"]}


class LanguageOrganizerTests(unittest.TestCase):
    def test_no_request_without_permission_or_configuration(self):
        calls = []
        def opener(*args, **kwargs):
            calls.append(args)
            raise AssertionError("No request should be made")
        for consent, key in [(False, "test-key"), (True, "")]:
            result, message = translate_notes("血检阳性", "Chinese", "Myself", consent=consent, api_key=key, model="test", opener=opener)
            self.assertIsNone(result)
            self.assertTrue(message)
        self.assertEqual(calls, [])

    def test_request_preserves_original_and_result_negation_timing_with_mock_response(self):
        def opener(req, **kwargs):
            payload = json.loads(req.data)
            self.assertFalse(payload["store"])
            source = json.loads(payload["input"][1]["content"])
            self.assertEqual(source["notes"], "血检阳性。两周后发病。")
            self.assertIn("positive/negative", payload["input"][0]["content"])
            return io.BytesIO(json.dumps({"output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(translated())}]}]}).encode())
        result, message = translate_notes("血检阳性。两周后发病。", "Chinese", "Myself", consent=True, api_key="test", model="test", opener=opener)
        self.assertFalse(message)
        self.assertIn("positive", result["timeline"]["tests"])
        self.assertIsNone(result["timeline"]["exposure"])
        self.assertIn("血检阳性", bilingual_text("血检阳性", "Chinese", "Myself", result))

    def test_malformed_or_failed_response_is_not_reported_as_translation(self):
        with self.assertRaises(ValueError):
            validate_translation({"english_translation": "Everything is fine"})
        def opener(*args, **kwargs):
            raise RuntimeError("SECRET provider body with PRIVATE STORY")
        result, message = translate_notes("PRIVATE STORY", "Other", "Myself", consent=True, api_key="SECRET", model="test", opener=opener)
        self.assertIsNone(result)
        self.assertNotIn("SECRET", message)
        self.assertNotIn("PRIVATE STORY", message)

    def test_summary_keeps_reported_tests_and_relative_timing_before_original(self):
        story = "I found a tick in Dutchess in July. Two weeks later I developed a rash and fever. My blood test was positive. It took four months to get a diagnosis."
        text = visit_summary_text(story, {})
        facts = story_details(story, {})
        self.assertIn("positive", facts["tests"])
        self.assertIn("Two weeks later", facts["onset"])
        self.assertIn("four months", facts["diagnosis"])
        self.assertLess(text.index("EXPOSURE AND CARE TIMELINE"), text.index("MY ORIGINAL NOTES"))
        self.assertEqual(story_details("I feel unwell.", {})["tick"], "")
        self.assertIn("negative", story_details("My Lyme blood test was negative.", {})["tests"])

    def test_shared_ui_requires_click_reuses_translation_and_hides_stale_result(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        with patch("language_organizer.translate_notes", return_value=(translated(), "")) as mocked:
            at = AppTest.from_file(str(app), default_timeout=60).run()
            at.button(key="route_ongoing").click().run()
            at.selectbox(key="notes_language").set_value("中文 / Chinese").run()
            at.text_area(key="quick_story_value").set_value("血检阳性。两周后发病。").run()
            self.assertTrue(at.button(key="translate_visit_notes").disabled)
            self.assertEqual(mocked.call_count, 0)
            at.checkbox(key="translation_consent").check().run()
            self.assertEqual(mocked.call_count, 0)
            at.button(key="translate_visit_notes").click().run()
            self.assertFalse(list(at.exception))
            self.assertEqual(mocked.call_count, 1)
            self.assertIn("positive blood test", at.text_area(key="bilingual_edit").value)
            at.button(key="care_to_tick_bite").click().run()
            self.assertFalse(list(at.exception))
            self.assertEqual(at.selectbox(key="notes_language").value, "中文 / Chinese")
            self.assertEqual(at.text_area(key="quick_story_value").value, "血检阳性。两周后发病。")
            self.assertTrue(any(d.key == "bilingual_download" for d in at.get("download_button")))
            self.assertEqual(mocked.call_count, 1)
            at.text_area(key="quick_story_value").set_value("新的笔记").run()
            self.assertFalse(any(d.key == "bilingual_download" for d in at.get("download_button")))
            self.assertTrue(any(d.key == "original_notes_download" for d in at.get("download_button")))
