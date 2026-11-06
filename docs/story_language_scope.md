# Clarify story-language selection

Review branch `fix/story-language-scope`, based on the published Japanese update. Not merged or deployed.

## Changes

- Rename the early selector to “Language for your story / 記録に使う言語”.
- Explain in English that the setting applies to writing a story, optional AI can prepare an English summary, and the rest of the app remains mainly English. Changing the setting does not delete or translate existing notes.
- For Japanese, show the scope explanation in Japanese before the English caption and offer “日本語で記録を始める →”.
- Reuse the existing visit organizer in a focused Care & Support entry route, with no new forms or storage. Let users continue to the full Care & Support workflow or return to homepage choices. Other homepage routes and sidebar navigation remain available.
- Preserve all 13 named language choices and existing consent requirements. No automatic AI request, new medical content, image content or changes to county data/calculations.

## Validation

13 focused regression tests passed: two new direct-entry/navigation tests, four Japanese persistence/PDF tests and seven existing organizer tests. Chromium browser checks passed at desktop 1440 px and mobile 390 px, covering the Japanese note/button, direct story entry, no UI exceptions and no horizontal document overflow at entry. No live API calls were made. `git diff --check` passed.

Screenshots: `docs/review/story_language_scope/entry_1440.png`, `entry_390.png`, `story_1440.png`, `story_390.png`.

Native Japanese wording review and live deployment verification remain outstanding. This is a story-language aid, not a full Japanese interface or certified medical translation.
