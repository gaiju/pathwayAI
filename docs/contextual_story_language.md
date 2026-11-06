# Contextual story-language entry

Review branch: `fix/contextual-story-language`. Based on published `9ea117f`. Not merged or deployed.

## Changes

The homepage keeps its existing hero and navigation and adds a bordered “Prefer to write in another language?” section before the pathway choices. It introduces writing in a comfortable language and downloading an English summary alongside the original. The existing language selector, scope note and Japanese direct-entry button live inside this section.

On subsequent pages, the language selector and scope explanation appear only in the story organizer, reused by Tick Bite, Care & Support and the focused story route. Prevention, Community Burden & Action, Feedback and other unrelated pages no longer show a story-language selector. There is one in-form language selector rather than an additional global selector.

All 13 named languages plus Other, original notes, burden fields, consent and existing downloads remain. Source data, calculations, AI payloads, symptoms/medical advice and other routes are unchanged. Refresh the cached language helper when the presentation revision changes so a running Streamlit process picks up this wording/layout.

## Validation

14 focused tests passed: one contextual-navigation test, four Japanese persistence/PDF tests, two direct-entry tests and seven organizer tests. The contextual test visits Prevention, Community and Feedback, confirms selectors are absent, returns to both story paths, changes language, returns home and verifies notes/preferences survive. No automatic translation requests occur.

Chromium checks passed at desktop 1440 px and mobile 390 px: welcoming homepage section, Japanese direct entry, no duplicate story-language selector, no UI exceptions, no horizontal document overflow. Screenshots are in `docs/review/contextual_language/`. `git diff --check` passed. No live API calls or real patient data were used. The full suite was not rerun for this presentation change.

## Scope limits

This is language support for writing and organizing a story, not a full translated interface. Japanese introductory language is still subject to native-reader review. Equivalent localized entry instructions for all other languages are not claimed. Preferences remain session-only. Deployment and live verification await approval.
