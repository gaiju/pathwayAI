"""Consistent branding for reports and shareable QR images; CSV data passes through unchanged."""
PERSONAL_PDF_LAYOUT_REVISION = 1
TAGLINE = "PathwayAI: Making the Hidden Patient Journey Visible—and Actionable"


def branded_qr(data):
    from io import BytesIO
    from pathlib import Path
    import reportlab
    from PIL import Image, ImageDraw, ImageFont
    original = Image.open(BytesIO(data)).convert("RGB")
    font = ImageFont.truetype(str(Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"), 18)
    width = max(640, original.width + 40)
    image = Image.new("RGB", (width, original.height + 125), "white")
    image.paste(original, ((width-original.width)//2, 20))
    draw = ImageDraw.Draw(image)
    lines = ["PathwayAI: Making the Hidden Patient Journey", "Visible—and Actionable"]
    for i,line in enumerate(lines):
        draw.text(((width-draw.textlength(line,font=font))/2, original.height+40+i*27), line, font=font, fill="#163149")
    output=BytesIO();image.save(output,format="PNG")
    return output.getvalue()


def branded_download_button(label, data, *args, **kwargs):
    import streamlit as st
    state_code = kwargs.pop("pdf_state_code", None)
    include_observations = kwargs.pop("include_daily_observations", False)
    compact = kwargs.pop("compact_personal_pdf", False)
    mime = kwargs.get("mime", "")
    name = kwargs.get("file_name", "")
    if mime == "text/plain" or str(name).lower().endswith((".txt", ".md")):
        binary = isinstance(data, bytes)
        text = data.decode("utf-8") if binary else data
        if include_observations:
            from daily_observations import session_observations_text
            text = session_observations_text(text)
        if isinstance(text, str) and TAGLINE not in text:
            text = TAGLINE + "\n\n" + text
        if compact:
            text = compact_personal_text(text)
        from pdf_report import report_pdf
        data = report_pdf(text, state_code=state_code) if state_code else report_pdf(text)
        from pathlib import Path
        kwargs["file_name"] = str(Path(name).with_suffix(".pdf")) if name else "PathwayAI_Report.pdf"
        kwargs["mime"] = "application/pdf"
    elif mime == "image/png" and "qr" in str(name).lower():
        data = branded_qr(data)
    return st.download_button(label, data, *args, **kwargs)


def personal_pdf_options(key):
    import streamlit as st
    with st.expander("PDF layout"):
        choice = st.radio("Choose your PDF layout", ["Full record", "Compact · hide unused fields"], key=key)
        st.caption("Compact keeps completed details and original notes. Unreported fields are omitted, not treated as No. Cost periods remain explicit.")
    return choice.startswith("Compact")


def compact_personal_text(text):
    """Remove explicit empty template fields, never source notes or negative findings."""
    import re
    keep = []
    omitted = False
    protected = False
    headings = {"STORY", "ORIGINAL NOTES", "ORIGINAL NOTES (UNCHANGED)", "MY ORIGINAL NOTES (FOR CROSS-CHECKING)", "FULL ENGLISH TRANSLATION"}
    # Work on blank-line-delimited sections to remove truly empty template sections.
    for block in re.split(r"\n\s*\n", text):
        lines = block.splitlines()
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped in headings:
                protected = True
            elif stripped in {"STRUCTURED JOURNEY", "BURDEN", "QUESTION FOR MY CLINICIAN",
                              "OPTIONAL TICK OBSERVATION (PATIENT-REPORTED, UNVERIFIED)",
                              "DATED DAILY-LIFE OBSERVATIONS", "EXPOSURE AND CARE TIMELINE",
                              "ENGLISH TIMELINE FOR REVIEW", "QUESTIONS TO CLARIFY", "MY QUESTIONS AND CORRECTIONS"}:
                protected = False
            missing = re.fullmatch(r"[^:\n]+:\s*Not reported[.]?", stripped, re.I)
            period = bool(re.search(r"\bperiod\b|\btime covered\b", stripped, re.I))
            if not protected and not period and (missing or stripped == "Not reported"):
                omitted = True
                continue
            cleaned.append(line)
        if cleaned and len(cleaned) == 1 and cleaned[0].strip().isupper() and cleaned[0].strip() not in headings and not protected:
            # An empty section heading left after removing its placeholders.
            omitted = True
            continue
        if cleaned:
            keep.append("\n".join(cleaned))
    if omitted:
        keep.insert(1, "Compact view: unused fields omitted. Missing information does not mean No.")
    return "\n\n".join(keep)
