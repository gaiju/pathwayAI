import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class ContextualLanguageTests(unittest.TestCase):
    def test_selector_lives_at_home_and_story_not_unrelated_pages(self):
        app=Path(__file__).resolve().parents[1]/'app.py'
        with patch('language_organizer.translate_notes') as translate:
            at=AppTest.from_file(str(app),default_timeout=60).run()
            self.assertTrue(any('Prefer to write in another language?' in item.value for item in at.markdown))
            at.selectbox(key='preferred_language_widget').set_value('日本語 / Japanese').run()
            at.button(key='start_story_language').click().run()
            self.assertEqual(at.selectbox(key='notes_language').value,'日本語 / Japanese')
            at.text_area(key='quick_story_value').set_value('架空の記録：検査は陰性でした。').run()
            for route in ('🛡️ Learn & Prevent','📊 Community Burden & Action','💬 Share Feedback'):
                at.sidebar.radio(key='pathway_view').set_value(route).run()
                keys=[item.key for item in at.selectbox]
                self.assertNotIn('preferred_language_widget',keys)
                self.assertNotIn('notes_language',keys)
                self.assertFalse(list(at.exception))
            at.sidebar.radio(key='pathway_view').set_value('🩹 Tick Bite: What Next?').run()
            self.assertEqual(at.selectbox(key='notes_language').value,'日本語 / Japanese')
            self.assertEqual(at.text_area(key='quick_story_value').value,'架空の記録：検査は陰性でした。')
            at.selectbox(key='notes_language').set_value('Русский / Russian').run()
            at.sidebar.radio(key='pathway_view').set_value('🧭 Care & Support').run()
            self.assertEqual(at.selectbox(key='notes_language').value,'Русский / Russian')
            at.button(key='change_path').click().run()
            self.assertEqual(at.selectbox(key='preferred_language_widget').value,'Русский / Russian')
            self.assertEqual(translate.call_count,0)
            self.assertFalse(list(at.exception))
