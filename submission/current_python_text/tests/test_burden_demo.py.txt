import csv
import io
import unittest

from burden_demo import fictional_cards, aggregate_demo, demo_summary_csv


class BurdenDemoTests(unittest.TestCase):
    def test_missing_fields_and_expected_summary(self):
        rows = {row["Measure"]: row for row in aggregate_demo(fictional_cards())}
        self.assertEqual(rows["Median missed workdays"]["Synthetic result"], "3")
        self.assertEqual(rows["Median unpaid caregiver hours"]["Synthetic result"], "6")
        self.assertEqual(rows["Medical OOP band"]["Usable examples"], 5)
        self.assertIn("$100–$499", rows["Medical OOP band"]["Synthetic result"])

    def test_small_groups_and_categories_are_withheld(self):
        self.assertTrue(all("Withheld" in row["Synthetic result"] for row in aggregate_demo(fictional_cards()[:4])))
        cards = fictional_cards()
        cards[-1]["barrier"] = "Appointment access"
        barrier = next(row for row in aggregate_demo(cards) if row["Measure"] == "Care barrier")
        self.assertIn("Withheld", barrier["Synthetic result"])

    def test_do_not_mix_period_phase_or_residence(self):
        for field, value in (("period", "Past 90 days"), ("phase", "After diagnosis"),
                             ("residence_fips", "36071")):
            cards = fictional_cards()
            cards[0][field] = value
            work = next(row for row in aggregate_demo(cards) if row["Measure"] == "Median missed workdays")
            self.assertEqual(work["Usable examples"], 4)
            self.assertIn("Withheld", work["Synthetic result"])

    def test_export_is_marked_synthetic_and_contains_no_individual_card(self):
        data = demo_summary_csv(aggregate_demo(fictional_cards())).decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(data)))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all("SYNTHETIC" in row["evidence_type"] for row in rows))
        self.assertNotIn("EXAMPLE-", data)


if __name__ == "__main__":
    unittest.main()
