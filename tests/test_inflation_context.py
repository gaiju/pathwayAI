import unittest
from pathlib import Path
from decimal import Decimal
from inflation_context import inflation_metadata, comparison_rows, export_rows, inflation_text

class InflationTests(unittest.TestCase):
    def test_missing_month_is_explicit_and_calculation_uses_available_observations(self):
        m=inflation_metadata()
        self.assertEqual((m['base_months'],m['target_months']),(12,11))
        self.assertEqual(m['missing_months'],['2025-10'])
        self.assertEqual(Decimal(m['target_index']),Decimal('321.943'))
        self.assertAlmostEqual(float(m['factor']),1.341389111297371)
        rows=comparison_rows()
        self.assertEqual(round(rows[2]['Restated · 2025 USD (11 months)']),2726)
        self.assertEqual(round(rows[-1]['Restated · 2025 USD (11 months)']),5516822)
        self.assertEqual(rows[-1]['Original · 2016 USD'],4112768)
        self.assertTrue(all(r['target_months']==11 and r['source_sha256'] for r in export_rows()))
        self.assertIn('not presented as a verified official annual-average',inflation_text())

    def test_ui_selects_comparison_without_changing_original_benchmarks(self):
        from streamlit.testing.v1 import AppTest
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'),default_timeout=60).run()
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.radio(key='journey_inflation_mode').value,'Original study dollars · 2016')
        at.radio(key='journey_inflation_mode').set_value('2025 purchasing power · general inflation').run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any('11 available monthly' in i.value for i in at.info))
        self.assertTrue(any(i.value=='$345–968 million' for i in at.metric))
        self.assertEqual(at.radio(key='county_inflation_mode').value,'Original study dollars · 2016')
