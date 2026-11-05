import unittest
from county_report_context import plan_context,map_metadata,county_location_map,regional_features
from county_burden_report import build_report,report_text
from mid_hudson_counties import COUNTIES
from pdf_report import _fonts

class CountyReportContextTests(unittest.TestCase):
    def test_dutchess_plan_not_assigned_to_other_counties(self):
        r=build_report('Dutchess','Getting to care')
        self.assertIn('830',r['county_plan_context']['findings'][1]['text'])
        self.assertIn('not Lyme',r['county_plan_context']['findings'][2]['text'])
        self.assertIn('no county endorsement',r['county_plan_context']['limits'])
        self.assertEqual(len(r['county_plan_context']['source_sha256']),64)
        self.assertIn('Fit with the Dutchess',report_text(r))
        for county in COUNTIES:
            if county!='Dutchess':
                other=build_report(county,'Getting to care')
                self.assertIsNone(other['county_plan_context'])
                self.assertNotIn('830 residents',report_text(other))

    def test_map_matches_selected_county_and_is_orientation_only(self):
        _fonts()
        self.assertEqual(set(regional_features()),set(COUNTIES.values()))
        for county,fips in COUNTIES.items():
            m=map_metadata(county)
            self.assertEqual(m['county_fips'],fips)
            self.assertIn('not disease risk',m['purpose'])
            drawing=county_location_map(county)
            self.assertIsNotNone(drawing)
            self.assertEqual(len(drawing.contents),9)
        with self.assertRaises(ValueError):county_location_map('Unknown')
