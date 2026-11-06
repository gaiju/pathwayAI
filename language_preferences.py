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


def show_language_choice():
    import streamlit as st
    language = st.session_state.get('saved_notes_language', 'English')
    if language not in LANGUAGES:
        language = 'Other / not sure'
    if 'preferred_language_widget' not in st.session_state:
        st.session_state['preferred_language_widget'] = language
    st.selectbox('Preferred language for notes and visit preparation / 記録に使う言語',
                 LANGUAGES, key='preferred_language_widget',
                 on_change=save_language_choice,
                 args=(st.session_state, 'preferred_language_widget'))
    st.caption('Menus remain mainly English. Choose your note language; changing it does not translate or delete your existing notes. AI translation requires your permission and a button click.')
    if st.session_state['preferred_language_widget'] == '日本語 / Japanese':
        st.caption('メニューは主に英語です。日本語と英語を混ぜて入力できます。言語を変えても元の記録は消えません。AI翻訳は同意してボタンを押した場合のみ行われます。')
