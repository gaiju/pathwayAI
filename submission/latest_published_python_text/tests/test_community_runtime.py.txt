import inspect
from pathlib import Path
import unittest
import county_burden_report
import county_planning_indicators
from community_runtime import ensure_current_community_modules


class CommunityRuntimeTests(unittest.TestCase):
    def test_cached_old_signature_is_replaced_before_ui_call(self):
        def old_report():
            pass
        county_burden_report.show_county_report = old_report
        county_burden_report._PATHWAYAI_COMMUNITY_SOURCE_SHA256 = 'old-release'
        with self.assertRaises(TypeError):
            county_burden_report.show_county_report(audience='Public health departments')
        ensure_current_community_modules()
        self.assertIn('audience', inspect.signature(county_burden_report.show_county_report).parameters)
        self.assertEqual(len(county_burden_report.COUNTIES), 7)
        report = county_burden_report.build_report('Putnam', 'Getting to care')
        self.assertEqual(report['reported_cases'], 294)

    def test_dependency_refresh_updates_bound_references_and_is_stable(self):
        county_planning_indicators.COUNTIES = {'Dutchess': '36027'}
        county_planning_indicators._PATHWAYAI_COMMUNITY_SOURCE_SHA256 = 'old-release'
        ensure_current_community_modules()
        self.assertEqual(len(county_planning_indicators.COUNTIES), 7)
        current = county_burden_report.show_county_report
        ensure_current_community_modules()
        self.assertIs(county_burden_report.show_county_report, current)

    def test_stale_module_does_not_break_navigation_or_clear_notes(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
        at.session_state['saved_story_text'] = 'PRIVATE_RELOAD_TEST'
        county_burden_report.show_county_report = lambda: None
        county_burden_report._PATHWAYAI_COMMUNITY_SOURCE_SHA256 = 'old-release'
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(len(at.selectbox(key='county_report_county').options), 7)
        self.assertEqual(at.session_state['saved_story_text'], 'PRIVATE_RELOAD_TEST')
        self.assertTrue(any(d.label == 'Download county burden & action report (PDF)' for d in at.get('download_button')))
