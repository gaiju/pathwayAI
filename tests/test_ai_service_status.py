import io
import json
import unittest
from urllib.error import HTTPError

from ai_service_status import classify_api_error


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


if __name__ == "__main__":
    unittest.main()
