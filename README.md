# PDF Text Extractor

A simple web app to extract text from any PDF — built with Streamlit and pypdf.

🔗 **Live app:** _add your streamlit.app link here after deploying_

## Features
- Upload any PDF, view extracted text instantly on the page
- Download the result as a `.txt` file
- Automatic fix for letter-spaced text (common in PDFs made with design tools like Canva)
- Handles empty-password-encrypted PDFs

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech stack
Python · Streamlit · pypdf
