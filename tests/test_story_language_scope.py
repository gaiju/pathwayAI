import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class StoryLanguageScopeTests(unittest.TestCase):
    def test_japanese_note_and_direct_story_entry_preserve_notes(self):
        app = Path(__file__).resolve().parents[1] / 'app.py'
        with patch('language_organizer.translate_notes') as translate:
            at = AppTest.from_file(str(app), default_timeout=60).run()
            self.assertEqual(at.selectbox(key='preferred_language_widget').label, 'Language for your story / 記録に使う言語')
            at.selectbox(key='preferred_language_widget').set_value('日本語 / Japanese').run()
            self.assertTrue(any('アプリ全体の表示言語は変わりません' in v.value for v in at.info))
            self.assertEqual(at.button(key='start_story_language').label, '日本語で記録を始める →')
            at.button(key='start_story_language').click().run()
            self.assertEqual(at.selectbox(key='notes_language').value, '日本語 / Japanese')
            self.assertFalse(any(h.value == '### 1. Find care' for h in at.markdown))
            at.text_area(key='quick_story_value').set_value('架空の例：検査は陰性でした。').run()
            at.button(key='story_to_care').click().run()
            self.assertEqual(at.text_area(key='quick_story_value').value, '架空の例：検査は陰性でした。')
            self.assertEqual(at.selectbox(key='notes_language').value, '日本語 / Japanese')
            self.assertEqual(translate.call_count, 0)
            self.assertFalse(list(at.exception))

    def test_english_direct_entry_does_not_remove_home_routes(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
        self.assertTrue(at.button(key='route_county'))
        self.assertTrue(at.button(key='route_bite'))
        at.button(key='start_story_language').click().run()
        self.assertTrue(at.text_area(key='quick_story_value'))
        at.button(key='story_to_choices').click().run()
        self.assertTrue(at.button(key='route_county'))
        self.assertFalse(list(at.exception))
