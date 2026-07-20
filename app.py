import re

import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="PDF Text Extractor", page_icon="📄", layout="centered")


def fix_letter_spacing(text: str) -> str:
    """
    Fix text extracted from PDFs (often ones made in Canva/design tools)
    where every character is separated by a space, e.g. 'H e l l o  W o r l d'.
    """
    fixed_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        tokens = stripped.split(" ")
        single_char_ratio = (
            sum(1 for t in tokens if len(t) <= 1) / len(tokens) if tokens else 0
        )
        if len(stripped) > 3 and single_char_ratio > 0.6:
            line = re.sub(r' {2,}', '\x00', line)
            line = line.replace(' ', '')
            line = line.replace('\x00', ' ')
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def extract_text_from_upload(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("PDF is encrypted/password-protected and could not be opened.")

    pages_text = []
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = fix_letter_spacing(text.strip())
        pages_text.append(f"\n{'=' * 60}\nPage {i} of {total_pages}\n{'=' * 60}\n{text}")

    return "\n".join(pages_text)


st.title("📄 PDF Text Extractor")
st.caption("Upload a PDF and get its extracted text — instantly, no signup.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        try:
            extracted = extract_text_from_upload(uploaded_file)
        except Exception as e:
            st.error(f"Couldn't extract text: {e}")
            extracted = None

    if extracted is not None:
        if not extracted.strip():
            st.warning("No extractable text found — this PDF may be scanned/image-based.")
        else:
            st.success("Text extracted successfully.")

        st.text_area("Extracted text", extracted, height=400)

        st.download_button(
            label="⬇️ Download as .txt",
            data=extracted,
            file_name=uploaded_file.name.rsplit(".", 1)[0] + ".txt",
            mime="text/plain",
        )
else:
    st.info("Upload a PDF above to get started.")

st.divider()
st.caption("Built with pypdf + Streamlit · by Muhammad Zeeshan")
