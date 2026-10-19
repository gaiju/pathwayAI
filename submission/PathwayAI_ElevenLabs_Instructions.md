# ElevenLabs narration

Use the file matching the selected ElevenLabs model:

- Eleven v3: PathwayAI_ElevenLabs_v3.txt. Uses [long pause] and [short pause]. These are model audio tags, not spoken headings. Durations are expressive rather than exact. Do not use SSML break tags with v3.
- Multilingual v2: PathwayAI_ElevenLabs_Multilingual_v2.txt. Contains only spoken text and inline <break time="..."/> tags. No <speak> wrapper or voice-direction prose is included.

Do not paste filenames, chapter headings, editing notes, [next slide] or [pause 3 seconds] into the speech text. Arbitrary bracketed directions may be spoken. Preview a short tagged passage in the selected model before generating the whole script; behavior can vary by voice and settings.

The black chapter cards require exactly three seconds in the final video. For v3, trim or extend silence in the video editor to match each card. A long-pause tag does not promise three seconds. Check v2 audio timing too. Do not add another three seconds on top of an existing three-second gap.

Generate, listen for pronunciation and naturalness, then check the final audio and silent cards together. Target about 4:45 and keep the complete video under 5:00. These files have not been rendered through ElevenLabs in this environment.
