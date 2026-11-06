"""One session language preference shared by entry and visit-note widgets."""
from language_organizer import LANGUAGES


def save_language_choice(state, widget):
    language = state.get(widget, 'English')
    if language not in LANGUAGES:
        language = 'Other / not sure'
    state['saved_notes_language'] = language
    other = 'notes_language' if widget == 'preferred_language_widget' else 'preferred_language_widget'
    state[other] = language
    # Existing source fingerprints also reject stale summaries. Drop the result
    # on an explicit language change so switching back does not revive it.
    for key in ('translation_result', 'translation_source', 'translation_error'):
        state.pop(key, None)


def show_language_choice(start_story=None):
    import streamlit as st
    language = st.session_state.get('saved_notes_language', 'English')
    if language not in LANGUAGES:
        language = 'Other / not sure'
    if 'preferred_language_widget' not in st.session_state:
        st.session_state['preferred_language_widget'] = language
    st.selectbox('Language for your story / 記録に使う言語',
                 LANGUAGES, key='preferred_language_widget',
                 on_change=save_language_choice,
                 args=(st.session_state, 'preferred_language_widget'))
    selected = st.session_state['preferred_language_widget']
    if selected == '日本語 / Japanese':
        st.info('この設定は、体験や症状を記録するための言語を選ぶものです。アプリ全体の表示言語は変わりません。メニューや他のページは主に英語です。日本語で入力できます。同意して翻訳ボタンを押すと、元の文章と英語の要約をダウンロードできます。')
    st.caption('Choose the language you’ll use to write your story. Optional AI can help prepare an English summary alongside your original notes. The app’s menus and other pages remain mainly in English. Changing this setting does not translate or delete your notes.')
    if start_story is not None:
        label = '日本語で記録を始める →' if selected == '日本語 / Japanese' else 'Start writing your story →'
        st.button(label, key='start_story_language', on_click=start_story)
