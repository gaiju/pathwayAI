"""Consistent report branding without changing data-table schemas or QR images."""
TAGLINE = "PathwayAI: Making the Hidden Patient Journey Visible—and Actionable"


def branded_download_button(label, data, *args, **kwargs):
    import streamlit as st
    mime = kwargs.get("mime", "")
    name = kwargs.get("file_name", "")
    if mime == "text/plain" or str(name).lower().endswith((".txt", ".md")):
        binary = isinstance(data, bytes)
        text = data.decode("utf-8") if binary else data
        if isinstance(text, str) and TAGLINE not in text:
            text = TAGLINE + "\n\n" + text
        data = text.encode("utf-8") if binary else text
    return st.download_button(label, data, *args, **kwargs)
