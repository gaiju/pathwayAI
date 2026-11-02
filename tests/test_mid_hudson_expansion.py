import json
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from mid_hudson_counties import COUNTIES, surveillance
from county_burden_report import build_report, report_text, report_csv_rows
from county_brief_pdf import county_brief_pdf
from streamlit.testing.v1 import AppTest
from pathlib import Path


class MidHudsonExpansionTests(unittest.TestCase):
    def test_seven_counties_preserve_verified_values_and_unknowns(self):
        self.assertEqual(len(COUNTIES), 7)
        expected={'Putnam':299.2,'Rockland':135.3,'Sullivan':482.6,'Ulster':461.2,'Westchester':113.2}
        counts={'Dutchess':1060,'Orange':964,'Putnam':294,'Rockland':461,'Sullivan':385,'Ulster':841,'Westchester':1125}
        for county in COUNTIES:
            for adjusted in (False,True):
                r=build_report(county,'Getting to care',adjusted)
                self.assertTrue(county_brief_pdf(r).startswith(b'%PDF'))
                self.assertEqual(r['county_fips'],COUNTIES[county])
                if county in expected:
                    self.assertEqual(r['reported_rate_per_100000'],expected[county])
                    self.assertEqual(r['reported_cases'],counts[county])
                    self.assertEqual(r['illustrative_total_2016_usd'],counts[county]*2032)
                    self.assertIsNone(r['additional_public_context']['language_context']['value'])
                    self.assertTrue(all(x['Reported cases per 100,000'] is None for x in r['additional_public_context']['rate_trend'][:2]))
                    self.assertNotIn('County economic illustration: USD 0',report_text(r))
                    if adjusted:self.assertGreater(r['inflation']['restated_total_usd'],r['illustrative_total_2016_usd'])
                    self.assertEqual(report_csv_rows(r)[0]['reported_cases'],counts[county])
                else:
                    self.assertEqual(r['illustrative_total_2016_usd'],r['reported_cases']*2032)
                self.assertTrue(all(v is not None for v in r['healthcare_context']['indicators'].values()))
        with self.assertRaises(ValueError):surveillance('Albany')

    def test_missing_count_stays_unknown_without_reconstruction(self):
        with TemporaryDirectory() as folder:
            missing=surveillance('Putnam',base=folder)
        self.assertIsNone(missing['reported_cases'])
        missing['reported_rate']=299.2
        with patch('county_burden_report.surveillance',return_value=missing):
            r=build_report('Putnam','Getting to care',True)
        self.assertIsNone(r['illustrative_total_2016_usd'])
        self.assertIsNone(r['inflation']['restated_total_usd'])
        self.assertTrue(county_brief_pdf(r).startswith(b'%PDF'))
        self.assertIn('no total is inferred from rates',r['formula'])

    def test_ui_changes_county_without_resetting_existing_comparisons(self):
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        at.button(key='route_county').click().run()
        self.assertEqual(at.selectbox(key='county_report_county').options,list(COUNTIES))
        for county in ['Putnam','Westchester','Orange']:
            at.selectbox(key='county_report_county').set_value(county).run()
            at.checkbox(key='county_report_inflation').check().run()
            self.assertFalse(list(at.exception))
            self.assertEqual(at.multiselect(key='county_comparisons_selected').value,['Reported Lyme rate','Language context'])
            self.assertTrue(any(d.label=='Download county burden & action report (PDF)' for d in at.get('download_button')))
