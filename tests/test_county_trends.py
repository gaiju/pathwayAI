import unittest

from county_trends import county_rate_trend


class ObservedTrendTests(unittest.TestCase):
    def test_joins_checked_years_and_excludes_definition_break(self):
        rows = county_rate_trend()
        self.assertEqual(len(rows), 9)
        self.assertEqual({row["Year"] for row in rows}, {2022, 2023, 2024})
        self.assertEqual({row["Area"] for row in rows}, {"Dutchess", "Orange", "New York State"})
        self.assertEqual(next(row["Reported cases per 100,000"] for row in rows
                              if row["Year"] == 2023 and row["Area"] == "Orange"), 296.9)
        for row in rows:
            self.assertEqual(row["evidence_type"], "reported_surveillance_rate")
            self.assertEqual(row["pdf_page"], 5 if row["Year"] == 2024 else 219)
            self.assertTrue(row["source_url"].endswith("rates.pdf" if row["Year"] == 2024 else "MHRCHA2025.pdf"))
