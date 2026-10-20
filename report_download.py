"""Consistent report branding without changing data-table schemas or QR images."""
TAGLINE = "PathwayAI: Making the Hidden Patient Journey Visible—and Actionable"


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
    return st.download_button(label, data, *args, **kwargs)
