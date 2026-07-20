import re

import pdfplumber
import streamlit as st

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


def format_table(table: list) -> str:
    """Format a table (list of rows, each a list of cells) as aligned pipe-separated text."""
    cleaned = [[(cell or "").strip() for cell in row] for row in table]
    if not cleaned:
        return ""
    col_count = max(len(row) for row in cleaned)
    col_widths = [0] * col_count
    for row in cleaned:
        for i in range(col_count):
            val = row[i] if i < len(row) else ""
            col_widths[i] = max(col_widths[i], len(val))

    lines = []
    for r, row in enumerate(cleaned):
        padded = [
            (row[i] if i < len(row) else "").ljust(col_widths[i])
            for i in range(col_count)
        ]
        lines.append("| " + " | ".join(padded) + " |")
        if r == 0:
            lines.append("|-" + "-|-".join("-" * w for w in col_widths) + "-|")
    return "\n".join(lines)


def extract_text_from_upload(uploaded_file) -> str:
    pages_output = []

    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages, start=1):
            section = [f"\n{'=' * 60}\nPage {i} of {total_pages}\n{'=' * 60}"]

            tables = page.find_tables()

            if tables:
                # Extract each detected table separately, formatted as rows/columns
                for t_idx, table_obj in enumerate(tables, start=1):
                    table_data = table_obj.extract()
                    if table_data:
                        section.append(f"\n[Table {t_idx}]")
                        section.append(format_table(table_data))

                # Also grab any text on the page that isn't part of a table
                # (e.g. headers, notes above/below the table)
                table_bboxes = [t.bbox for t in tables]
                non_table_text = page.filter(
                    lambda obj: not any(
                        obj.get("top", -1) >= bbox[1] and obj.get("bottom", -1) <= bbox[3]
                        and obj.get("x0", -1) >= bbox[0] and obj.get("x1", -1) <= bbox[2]
                        for bbox in table_bboxes
                    )
                ).extract_text() or ""
                non_table_text = fix_letter_spacing(non_table_text.strip())
                if non_table_text:
                    section.append("\n[Other text on page]")
                    section.append(non_table_text)
            else:
                text = page.extract_text() or ""
                text = fix_letter_spacing(text.strip())
                section.append(text)

            pages_output.append("\n".join(section))

    return "\n".join(pages_output)


st.title("📄 PDF Text Extractor")
st.caption("Upload a PDF and get its extracted text — tables come out as rows and columns, regular text stays plain.")

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
st.caption("Built with pdfplumber + Streamlit · by Muhammad Zeeshan")
