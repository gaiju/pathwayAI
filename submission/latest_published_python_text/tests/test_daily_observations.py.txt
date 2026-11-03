from datetime import date
from pathlib import Path
import unittest
from unittest.mock import patch
from daily_observations import normalize_observation, observation_rows, observations_text, append_observations


class DailyObservationTests(unittest.TestCase):
    def test_unknown_zero_dates_and_overlapping_periods_are_not_summed(self):
        first = normalize_observation({'date': date(2026, 10, 1), 'period': 'Past 7 days', 'caregiver_hours': 8, 'work_impact': 'Reduced hours'})
        second = normalize_observation({'date': date(2026, 10, 3), 'period': 'Past 7 days', 'caregiver_hours': 0})
        unknown = normalize_observation({})
        self.assertEqual(first['date'], '2026-10-01')
        rows = observation_rows([unknown, second, first])
        self.assertEqual([r['Caregiving hours'] for r in rows], ['8','0','Not reported'])
        text = observations_text([first, second, unknown])
        self.assertIn('Periods may overlap', text)
        self.assertNotIn('Total caregiving', text)
        self.assertEqual(append_observations(text, [first]), text)
        self.assertEqual(append_observations('Private record', [first], include=False), 'Private record')
        for value in [-1, float('nan'), float('inf'), True]:
            with self.assertRaises(ValueError): normalize_observation({'caregiver_hours': value})

    def test_app_saves_observation_and_retains_it_across_navigation_and_clear(self):
        from streamlit.testing.v1 import AppTest
        app=Path(__file__).resolve().parents[1]/'app.py'
        at=AppTest.from_file(str(app), default_timeout=60).run()
        at.button(key='route_ongoing').click().run()
        at.number_input(key='medical88').set_value(123).run()
        at.date_input(key='observation_date').set_value(date(2026,10,1))
        at.selectbox(key='observation_period').set_value('Past 7 days')
        at.selectbox(key='observation_work_impact').set_value('Reduced hours')
        at.number_input(key='observation_caregiver_hours').set_value(8)
        at.text_input(key='observation_support_needed').set_value('Transport help')
        at.button(key='add_daily_observation').click().run()
        self.assertFalse(list(at.exception))
        obs=at.session_state['daily_life_observations']
        self.assertEqual(len(obs),1)
        self.assertEqual(obs[0]['caregiver_hours'],8)
        self.assertEqual(at.number_input(key='medical88').value,123)
        self.assertIn('DATED DAILY-LIFE OBSERVATIONS',at.text_area(key='summary88_text').value)
        at.checkbox(key='include_daily_observations').uncheck().run()
        self.assertNotIn('DATED DAILY-LIFE OBSERVATIONS',at.text_area(key='summary88_text').value)
        at.button(key='patient_to_community').click().run()
        self.assertEqual(len(at.session_state['daily_life_observations']),1)
        at.button(key='community_cost_record').click().run()
        self.assertFalse(list(at.exception))
        self.assertFalse(at.checkbox(key='include_daily_observations').value)
        self.assertEqual(at.number_input(key='medical88').value,123)
        at.checkbox(key='include_daily_observations').check().run()
        self.assertIn('Transport help',at.text_area(key='summary88_text').value)
        at.button(key='remove_daily_observation').click().run()
        self.assertEqual(len(at.session_state['daily_life_observations']),0)
        self.assertNotIn('DATED DAILY-LIFE OBSERVATIONS',at.text_area(key='summary88_text').value)
        at.button(key='clear_session77').click().run()
        self.assertNotIn('daily_life_observations',at.session_state)

    def test_private_timeline_is_only_added_to_explicit_personal_downloads(self):
        from report_download import branded_download_button
        from streamlit.testing.v1 import AppTest
        from daily_observations import session_observations_text
        # Verify output routing using a controlled session lookup; public exports never request attachment.
        with patch('streamlit.download_button') as dl, patch('pdf_report.report_pdf', return_value=b'%PDF-test') as pdf, patch('daily_observations.session_observations_text', side_effect=lambda s:s+'\nPRIVATE_TIMELINE'):
            branded_download_button('Personal','Notes',mime='text/plain',file_name='record.txt', include_daily_observations=True)
            self.assertIn('PRIVATE_TIMELINE',pdf.call_args.args[0])
            branded_download_button('Public','Methods',mime='text/plain',file_name='methods.txt')
            self.assertNotIn('PRIVATE_TIMELINE',pdf.call_args.args[0])
