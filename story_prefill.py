import re
import math

def story_burden_defaults88(story):
    """Copy only single, explicit amounts/counts.

    Every candidate (including “and another”) passes the same validation.
    Multiple or uncertain amounts are left blank with a note.
    Medical amounts require explicit patient-payment language.
    Workdays require the patient as subject (“I missed”).
    """
    text = (story or "").strip()
    number_words = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    count = r"(?P<value>\d{1,4}|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
    money = r"\$\s*(?P<value>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)(?!\d)"
    paid = r"\bi\s+(?:also\s+)?(?:paid|spent)\s+(?:a total of\s+)?"

    patterns = {
        "medical88": [
            paid + money + r"\s+(?:out[- ]of[- ]pocket\s+)?(?:for|on|in)\s+(?:my\s+)?(?:medical care|medical bills?|healthcare|doctor|specialist|testing|labs?)\b",
            r"(?:and|plus)\s+(?:another\s+)?" + money + r"\s+(?:for|on|in)\s+(?:my\s+)?medical(?: care| bills?)?\b",
        ],
        "other88": [
            paid + money + r"\s+(?:for|on|in)\s+(?:my\s+)?(?:travel(?: and lodging)?|transport(?:ation)?|lodging|nonmedical expenses|other expenses)\b",
            r"\b(?:my\s+)?(?:travel(?: and lodging)?|transport(?:ation)?|lodging|nonmedical|other) (?:costs?|expenses)\s*(?:were|was|totaled|totalled|came to|:|=)\s*" + money,
            r"(?:and|plus)\s+(?:another\s+)?" + money + r"\s+(?:for|on|in)\s+(?:my\s+)?(?:travel|transport(?:ation)?|lodging)\b",
        ],
        "workdays88": [
            r"\bi\s+missed\s+" + count + r"\s+(?:workdays?|days? (?:of|from) work)\b",
            r"\bi\s+(?:missed work|was off work|could not work|couldn't work)\s+for\s+" + count + r"\s+days?\b",
            r"\b(?:and|plus)\s+(?:another\s+)?" + count + r"\s+(?:workdays?|days? (?:of|from) work)\b",
        ],
        "caregiver88": [
            r"\b(?:my\s+)?unpaid caregiver\s+(?:spent|provided)\s+" + count + r"\s+hours?\b",
            r"\bunpaid caregiv(?:ing|er) (?:time|help)\s*(?:was|totaled|totalled|:|=)\s*" + count + r"\s+hours?\b",
        ],
    }

    def sentence_bounds(pos):
        start = 0
        for m in re.finditer(r"[.!?]\s|\n", text[:pos]):
            if text[m.start()] == "." and m.start() > 0 and m.start()+1 < len(text):
                if text[m.start()-1].isdigit() and text[m.start()+1].isdigit():
                    continue
            start=m.end()
        end=len(text)
        for m in re.finditer(r"[.!?]\s|\n", text[pos:]):
            abs_pos=pos+m.start()
            if text[abs_pos] == "." and abs_pos > 0 and abs_pos+1 < len(text):
                if text[abs_pos-1].isdigit() and text[abs_pos+1].isdigit():
                    continue
            end=pos+m.start()
            break
        return start,end

    def valid_value(key, match):
        start, end = sentence_bounds(match.start())
        clause = text[start:end]
        prefix = clause[: match.start() - start]
        if re.search(
            r"\b(?:not|never|didn't|haven't|hadn't|might|may|would|could|if|estimate|estimated|about|around|approximately|up to|more than|less than)\b",
            prefix, re.I,
        ):
            return None
        if re.search(
            r"\b(?:insurer|insurance|medicare|medicaid|employer)\s+(?:paid|covered|reimbursed)\b",
            clause, re.I,
        ):
            return None
        suffix = text[match.end() : match.end() + 40]
        if re.match(
            r"\s*(?:per\b|each\b|every\b|a (?:day|week|month|visit)\b|to\s+\$?\d|[-–]\s*\$?\d)",
            suffix, re.I,
        ):
            return None
        token = match.group("value").lower().replace(",", "")
        try:
            value = number_words[token] if token in number_words else float(token)
        except ValueError:
            return None
        if not math.isfinite(value) or value < 0:
            return None
        if key == "workdays88" and value > 3650:
            return None
        matched_text = match.group(0)
        if key in ("medical88", "other88") and re.search(r"(?:and|plus)\s+(?:another\s+)?\$", matched_text, re.I):
            if not re.search(r"\bi\s+(?:also\s+)?(?:paid|spent)\b", text[start:match.start()], re.I):
                return None
        if key == "workdays88" and re.search(r"(?:and|plus)\s+(?:another\s+)?", matched_text, re.I):
            if not re.search(r"\bi\s+(?:missed|was off|could not|couldn't)\b", text[start:match.start()], re.I):
                return None
        return int(value) if key in ("workdays88", "caregiver88") else float(value)

    defaults, notes = {}, {}
    for key, expressions in patterns.items():
        matches = {}
        for expression in expressions:
            for match in re.finditer(expression, text, re.I):
                value = valid_value(key, match)
                if value is not None:
                    matches[match.span("value")] = value

        # Same-category “and another” ambiguity → force multi-match note
        and_another_spans = [
            span for span in matches
            if re.search(r"(?:and|plus)\s+(?:another\s+)?(?:\$|\d)", text[max(0, span[0]-25):span[0]+1], re.I)
        ]
        if and_another_spans:
            for span in and_another_spans:
                start, _ = sentence_bounds(span[0])
                bare_pat = money if key != "workdays88" else count
                for bm in re.finditer(bare_pat, text[start:span[0]], re.I):
                    abs_span = (start + bm.start("value"), start + bm.end("value"))
                    if abs_span in matches:
                        continue
                    after = text[start + bm.end() : span[0]]
                    if key == "medical88" and re.search(r"\b(?:travel|transport|lodging)\b", after, re.I):
                        continue
                    if key == "other88" and re.search(r"\bmedical\b", after, re.I):
                        continue
                    token = bm.group("value").lower().replace(",", "")
                    try:
                        value = number_words[token] if token in number_words else float(token)
                    except ValueError:
                        continue
                    if math.isfinite(value) and value >= 0:
                        matches[abs_span] = value

        if len(matches) == 1:
            defaults[key] = next(iter(matches.values()))
        elif len(matches) > 1:
            notes[key] = "Please review and enter the amount."
    return defaults, notes


def apply_story_burden_defaults88(state, defaults):
    """Refresh untouched prefills while preserving patient corrections, including blanks."""
    previous = state.get("story_burden_prefills88", {})
    edited = set(state.get("story_burden_edited88", []))
    applied = {}
    for key in ("medical88", "other88", "workdays88", "caregiver88"):
        current = state.get(key)
        if key in previous and key in state and current != previous[key]:
            edited.add(key)
        elif key in state and current is not None and key not in previous:
            edited.add(key)
        if key in edited:
            continue
        can_copy = key not in state or current is None or (key in previous and current == previous[key])
        if can_copy and key in defaults:
            state[key] = defaults[key]
            applied[key] = defaults[key]
        elif key in previous and current == previous[key]:
            state[key] = None
    state["story_burden_prefills88"] = applied
    state["story_burden_edited88"] = sorted(edited)
    return applied

