import io
import json
import unittest
from urllib.error import HTTPError

from ai_service_status import classify_api_error, log_transport_error
from urllib.error import URLError


class APIStatusTests(unittest.TestCase):
    def error(self, status, body):
        return HTTPError("https://api.openai.com/v1/responses", status,
                         "failure", {}, io.BytesIO(body))

    def test_exhausted_quota_is_distinct_from_temporary_throttling(self):
        quota = self.error(429, json.dumps({"error": {
            "code": "insufficient_quota", "message": "private account details"
        }}).encode())
        notice = classify_api_error(quota)
        self.assertEqual(notice["kind"], "quota")
        self.assertNotIn("private account details", notice["message"])
        busy = self.error(429, b'{"error":{"code":"rate_limit_exceeded"}}')
        self.assertEqual(classify_api_error(busy)["kind"], "rate_limit")

    def test_billing_limit_and_inactive_billing(self):
        for code in ("billing_hard_limit_reached", "billing_not_active"):
            with self.subTest(code=code):
                error = self.error(400, json.dumps({"error": {"type": code}}).encode())
                self.assertEqual(classify_api_error(error)["kind"], "quota")

    def test_malformed_provider_responses_do_not_leak_or_crash(self):
        for body in (b'not json', b'null', b'{"error":null}', b'\xff'):
            with self.subTest(body=body):
                self.assertEqual(classify_api_error(self.error(502, body))["kind"], "unavailable")

    def test_diagnostic_logs_allowlisted_code_not_sensitive_details(self):
        error = self.error(401, json.dumps({"error": {
            "code": "invalid_api_key", "message": "SECRET_KEY PATIENT_STORY"
        }}).encode())
        with self.assertLogs("pathwayai.ai_service", level="WARNING") as captured:
            classify_api_error(error)
        text = " ".join(captured.output)
        self.assertIn("http_status=401 error_code=invalid_api_key", text)
        self.assertNotIn("SECRET_KEY", text)
        self.assertNotIn("PATIENT_STORY", text)

    def test_untrusted_codes_and_types_cannot_enter_logs(self):
        for code in ("PRIVATE_NOTE\nforged log", ["PRIVATE_NOTE"], {"secret": "PRIVATE_NOTE"}):
            error = self.error(400, json.dumps({"error": {"code": code, "type": code}}).encode())
            with self.assertLogs("pathwayai.ai_service", level="WARNING") as captured:
                classify_api_error(error)
            self.assertIn("error_code=unrecognized", captured.output[0])
            self.assertNotIn("PRIVATE_NOTE", " ".join(captured.output))

    def test_transport_logs_do_not_include_exception_message(self):
        for error, code in [(TimeoutError("SECRET_KEY"), "timeout"),
                            (URLError("PRIVATE_STORY"), "connection_error")]:
            with self.assertLogs("pathwayai.ai_service", level="WARNING") as captured:
                log_transport_error(error)
            self.assertIn("error_code="+code, captured.output[0])
            self.assertNotIn("SECRET_KEY", " ".join(captured.output))
            self.assertNotIn("PRIVATE_STORY", " ".join(captured.output))

    def test_app_wrapper_records_failure_without_extra_api_requests(self):
        import ast
        import sqlite3
        import urllib.request
        import urllib.error
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        source = Path(__file__).resolve().parents[1] / "app.py"
        tree = ast.parse(source.read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_limited_ai_urlopen")
        state = {}
        scope = dict(st=SimpleNamespace(session_state=state), MAX_AI_CALLS_PER_SESSION=5,
                     AIRateLimitError=RuntimeError, _ai_quota=lambda *a, **kw: (True, ""),
                     _ai_bucket=lambda: "fake", Path=Path, __file__=str(source),
                     sqlite3=sqlite3, urllib=__import__("urllib"),
                     classify_api_error=classify_api_error, log_transport_error=log_transport_error,
                     show_ai_service_notice=lambda: None)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), scope)
        with patch("urllib.request.urlopen", side_effect=self.error(403, b'{"error":{"code":"permission_denied"}}')) as opener:
            with self.assertLogs("pathwayai.ai_service", level="WARNING") as captured:
                with self.assertRaises(RuntimeError): scope["_limited_ai_urlopen"](object())
            opener.assert_called_once()
            self.assertIn("http_status=403 error_code=permission_denied", captured.output[0])
        self.assertEqual(state["pathwayai_ai_calls"], 1)
        with patch("urllib.request.urlopen", side_effect=URLError("PRIVATE")) as opener:
            with self.assertLogs("pathwayai.ai_service", level="WARNING"):
                with self.assertRaises(URLError): scope["_limited_ai_urlopen"](object())
            opener.assert_called_once()


if __name__ == "__main__":
    unittest.main()
