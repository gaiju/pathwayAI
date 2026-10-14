import unittest

from county_cost_scenario import county_scenario


class CountyScenarioTests(unittest.TestCase):
    def test_overall_mean_and_population_rate_scaling(self):
        rows = county_scenario()
        self.assertEqual(rows[0]["Illustrative medical amount · 2022 USD"], 1060 * 2227)
        self.assertEqual(rows[1]["Illustrative amount per 100,000 · 2022 USD"], 237 * 2227)
        self.assertIsNone(rows[0]["assumed_disseminated_share"])

    def test_zero_full_and_mixed_shares(self):
        self.assertEqual(county_scenario(0)[0]["Medical reference per episode · 2022 USD"], 695)
        self.assertEqual(county_scenario(1)[0]["Medical reference per episode · 2022 USD"], 6833)
        self.assertEqual(county_scenario(.5)[0]["Medical reference per episode · 2022 USD"], (695 + 6833) / 2)

    def test_invalid_assumptions_fail_and_exports_keep_limits(self):
        for share in (-.1, 1.1, float("nan"), True):
            with self.assertRaises(ValueError):
                county_scenario(share)
        row = county_scenario()[0]
        self.assertIn("illustrative", row["scenario_type"])
        self.assertIn("OOP not added", row["limits"])
        self.assertTrue(row["case_source"].startswith("https://www.health.ny.gov/"))


if __name__ == "__main__":
    unittest.main()
