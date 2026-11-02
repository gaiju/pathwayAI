import json
from tempfile import TemporaryDirectory
import unittest
from county_planning_indicators import planning_indicators, planning_context_text, socioeconomic_context
from county_burden_report import build_report, report_text, report_csv_rows


class CountyPlanningIndicatorTests(unittest.TestCase):
    def test_comparison_trend_and_language_match_existing_sources(self):
        dutchess = planning_indicators('Dutchess')
        orange = planning_indicators('Orange')
        self.assertEqual([r['Reported cases'] for r in dutchess['comparison']], [1060, 964, 21632])
        self.assertEqual([r['Reported cases per 100,000'] for r in dutchess['rate_trend']], [394.6, 358.9, 355.5])
        self.assertEqual([r['Reported cases per 100,000'] for r in orange['rate_trend']], [231.6, 296.9, 237.0])
        self.assertEqual(dutchess['language_context']['value'], 16.2)
        self.assertEqual(orange['language_context']['value'], 30.2)
        self.assertEqual([row['value'] for row in dutchess['socioeconomic_context']], [4.7, 8.0])
        self.assertEqual([row['value'] for row in orange['socioeconomic_context']], [5.5, 12.7])
        self.assertEqual([row['year'] for row in orange['socioeconomic_context']], [2022, 2023])
        self.assertEqual(len(dutchess['listed_initiatives']), 3)
        self.assertEqual(orange['listed_initiatives'], [])
        self.assertIn('No listing does not mean no services', orange['initiative_status'])

    def test_missing_values_are_not_filled_from_other_counties_or_zero(self):
        with TemporaryDirectory() as folder:
            context = planning_indicators('Orange', base=folder)
            self.assertTrue(all(row['Reported cases'] is None for row in context['comparison']))
            self.assertTrue(all(row['Reported cases per 100,000'] is None for row in context['rate_trend']))
            self.assertIn('Not available', planning_context_text(context))
            self.assertEqual(context['listed_initiatives'], [])
            self.assertTrue(all(row['value'] is None for row in context['socioeconomic_context']))
        with self.assertRaises(ValueError):
            planning_indicators('Unsupported')

    def test_exports_keep_selected_county_and_original_cost_arithmetic(self):
        for county, count in [('Dutchess', 1060), ('Orange', 964)]:
            report = build_report(county, 'Getting to care', True)
            self.assertEqual(report['illustrative_total_2016_usd'], count*2032)
            context = json.loads(report_csv_rows(report)[0]['additional_public_context'])
            self.assertEqual(context['county'], county)
            self.assertIn(county+' reported-rate trend', report_text(report))
            self.assertIn('Not a measure of English proficiency', report_text(report))
            self.assertIn('self-selected', report_text(report))
            self.assertEqual(len({s['url'] for s in report['sources']}), len(report['sources']))
