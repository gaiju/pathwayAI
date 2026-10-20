"""Consistent branding for reports, CSV metadata and shareable QR images."""
TAGLINE = "PathwayAI: Making the Hidden Patient Journey Visible—and Actionable"


def branded_csv(data):
    import csv
    from io import StringIO
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data.lstrip("\ufeff")
    reader = csv.DictReader(StringIO(text))
    fields = list(reader.fieldnames or [])
    if "PathwayAI report" not in fields:
        fields.append("PathwayAI report")
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in reader:
        row["PathwayAI report"] = TAGLINE
        writer.writerow(row)
    return output.getvalue().encode("utf-8-sig")


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
    mime = kwargs.get("mime", "")
    name = kwargs.get("file_name", "")
    if mime == "text/plain" or str(name).lower().endswith((".txt", ".md")):
        binary = isinstance(data, bytes)
        text = data.decode("utf-8") if binary else data
        if isinstance(text, str) and TAGLINE not in text:
            text = TAGLINE + "\n\n" + text
        from pdf_report import report_pdf
        data = report_pdf(text, state_code=state_code) if state_code else report_pdf(text)
        from pathlib import Path
        kwargs["file_name"] = str(Path(name).with_suffix(".pdf")) if name else "PathwayAI_Report.pdf"
        kwargs["mime"] = "application/pdf"
    elif mime == "text/csv":
        data = branded_csv(data)
    elif mime == "image/png" and "qr" in str(name).lower():
        data = branded_qr(data)
    return st.download_button(label, data, *args, **kwargs)
