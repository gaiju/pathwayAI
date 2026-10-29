"""Privacy practices must be visible before story input on both entry paths."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'


class StoryPrivacyTests(unittest.TestCase):
    def test_notice_reflects_collection_flag_without_promising_deletion(self):
        tree = ast.parse(APP.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'show_story_privacy_notice')
        code = compile(ast.Module(body=[function], type_ignores=[]), str(APP), 'exec')
        for enabled in (False, True):
            st = Mock()
            scope = {'st': st, 'PATIENT_VOICE_STORAGE_ENABLED': enabled}
            exec(code, scope)
            scope['show_story_privacy_notice']()
            text = '\n'.join(str(c.args[0]) for c in st.method_calls)
            self.assertIn('fictional information', text)
            self.assertIn('does not guarantee zero retention', text)
            self.assertIn('retention remain unverified', text)
            self.assertIn('require separate consent' if enabled else
                          'collection is disabled', text)
            st.expander.assert_not_called()

    def test_both_routes_show_notice_before_input_and_preserve_local_choice(self):
        for route in ('route_bite', 'route_ongoing'):
            with self.subTest(route=route):
                at = AppTest.from_file(str(APP), default_timeout=60).run()
                at.button(key=route).click().run()
                self.assertFalse(list(at.exception))
                elements = list(at.main)
                notice = next(i for i, e in enumerate(elements)
                              if e.type == 'caption' and 'Before sharing:' in e.value)
                story = next(i for i, e in enumerate(elements)
                             if e.type == 'text_area' and e.key == 'quick_story_value')
                self.assertLess(notice, story)
                self.assertFalse(at.checkbox(key='use_story_ai65').value)
                at.text_area(key='quick_story_value').set_value('Fictional note for testing.').run()
                self.assertFalse(list(at.exception))
                self.assertTrue(any('server-side app session' in e.value for e in at.caption))
                at.button(key='clear_session77').click().run()
                self.assertFalse(list(at.exception))
                self.assertNotIn('saved_story_text', at.session_state)
