import json
import unittest
from pathlib import Path
from county_burden_report import build_report, report_text, report_csv_rows
from community_action import ACTION_OPTIONS

class CountyReportTests(unittest.TestCase):
    def test_sources_arithmetic_and_optional_restatement_stay_separate(self):
        priority=next(iter(ACTION_OPTIONS))
        for county,count in [('Dutchess',1060),('Orange',964)]:
            r=build_report(county,priority)
            self.assertEqual(r['reported_cases'],count)
            self.assertEqual(r['illustrative_total_2016_usd'],count*2032)
            self.assertIsNone(r['inflation'])
            self.assertTrue(all(s['url'].startswith('https://') for s in r['sources']))
            adjusted=build_report(county,priority,True)
            self.assertEqual(adjusted['inflation']['target_months'],11)
            self.assertEqual(adjusted['illustrative_total_2016_usd'],count*2032)
            self.assertIn('October is missing',report_text(adjusted))
            exported=report_csv_rows(adjusted)[0]
            self.assertEqual(json.loads(exported['inflation'])['target_months'],11)

    def test_planning_is_proposed_and_private_session_records_are_excluded(self):
        from streamlit.testing.v1 import AppTest
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        at.session_state['saved_story_text']='PRIVATE_REPORT_SENTINEL'
        at.session_state['daily_life_observations']=[{'support_needed':'PRIVATE_OBSERVATION_SENTINEL'}]
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        at.selectbox(key='county_report_county').set_value('Orange').run()
        at.selectbox(key='county_report_priority').set_value('Getting to care').run()
        at.checkbox(key='county_report_inflation').check().run()
        self.assertFalse(list(at.exception))
        r=build_report('Orange','Getting to care',True)
        text=report_text(r)
        self.assertNotIn('PRIVATE_REPORT_SENTINEL',text)
        self.assertNotIn('PRIVATE_OBSERVATION_SENTINEL',json.dumps(report_csv_rows(r)))
        self.assertIn('not findings about local demand',text)
        self.assertIn('Requested and completed accessible rides',text)
        self.assertTrue(any(x.label=='Download county burden & action report (PDF)' for x in at.get('download_button')))
