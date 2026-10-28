"""Community discovery, source consistency and public PDF regressions."""
import re
import unittest
from pathlib import Path

from county_evidence import county_surveillance, state_surveillance, healthcare_capacity, _number
from county_burden_report import build_report
from county_report_pdf import county_report_pdf
from county_cost_scenario import county_scenario


class HudsonCommunityTests(unittest.TestCase):
    def test_registry_agrees_with_reports_and_missing_values_stay_unknown(self):
        self.assertEqual(_number(0),0)
        self.assertIsNone(_number(None))
        self.assertIsNone(_number(float('nan')))
        self.assertIsNone(_number('not available'))
        for row in county_surveillance():
            report=build_report(row['county'],'Getting to care')
            old=next(x for x in county_scenario(perspective='societal') if x['County']==row['county'])
            self.assertEqual(report['reported_cases'],row['reported_cases'])
            self.assertEqual(report['illustrative_total_2016_usd'],old['Illustrative societal amount · 2016 USD'])
            self.assertEqual(report['state_reported_rate_per_100000'],state_surveillance()['reported_rate'])
            self.assertIn('not independently verified',report['denominator_status'])
            self.assertEqual(report['local_context']['healthcare']['year'],2023)
            self.assertEqual({x['county'] for x in report['comparison']},{'Dutchess','Orange','New York State'})

    def test_structured_brief_is_two_pages_and_has_real_source_annotations(self):
        for county in ['Dutchess','Orange']:
            for restate in [False,True]:
                report=build_report(county,'Unpaid care and daily life',restate)
                data=county_report_pdf(report)
                self.assertTrue(data.startswith(b'%PDF'))
                self.assertEqual(len(re.findall(rb'/Type /Page\b',data)),2)
                self.assertIn(b'/Annots',data)
                self.assertGreaterEqual(data.count(b'/URI'),len(report['sources']))
                self.assertIn(b'www.health.ny.gov',data)

    def test_landing_opens_regional_demo_and_retains_all_patient_paths(self):
        from streamlit.testing.v1 import AppTest
        app=Path(__file__).resolve().parents[1]/'app.py'
        at=AppTest.from_file(str(app),default_timeout=60).run()
        self.assertEqual(at.button(key='route_county').label,'Explore Hudson Valley Burden & Action')
        self.assertTrue(all(at.button(key=k) for k in ['route_bite','route_ongoing','route_outdoors','route_feedback']))
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual([t.label for t in at.tabs],['Region','Compare','Burden','Plan'])
        self.assertTrue(any('A Hudson Valley starting point' in x.value for x in at.markdown))
        self.assertTrue(any('Other Hudson Valley counties are not yet included' in x.value for x in at.markdown))
        self.assertFalse(next(x for x in at.expander if x.label=='Additional planning templates').proto.expanded)
        self.assertFalse(next(x for x in at.expander if x.label=='New York map and tick observations').proto.expanded)
        at.multiselect(key='county_comparisons_selected').set_value(['Reported Lyme rate','Language context','Disability context']).run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any('underlying Census year is unresolved' in x.value for x in at.caption))
        at.button(key='community_cost_record').click().run()
        self.assertEqual(at.radio(key='pathway_view').value,'🧭 Care & Support')
        self.assertFalse(list(at.exception))
