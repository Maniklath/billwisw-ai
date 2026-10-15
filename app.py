
import re
import streamlit as st
import pymupdf
import pytesseract
from PIL import Image
from io import BytesIO

# Windows par Tesseract ka path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

st.set_page_config(
    page_title="BillWise AI",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 BillWise AI")
st.subheader("Intelligent Invoice & Expense Analyzer")
st.write("Upload an invoice to extract its details automatically.")


def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else "Not found"



def extract_vendor(text):
    # First try an explicit Vendor: label
    vendor = extract_field(
        text, r"^\s*Vendor\s*:\s*(.+)$"
    )

    if vendor != "Not found":
        return vendor

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Skip common invoice headings and metadata
    skip = re.compile(
        r"tax invoice|invoice|bill to|ship to|"
        r"date|due date|number|gstin|phone|email|"
        r"purchase order|payment terms|^\d",
        re.IGNORECASE
    )

    company_suffix = re.compile(
        r"\b(private limited|pvt\.?\s*ltd\.?|"
        r"limited|ltd\.?|inc\.?|llc|llp|corp\.?)\b",
        re.IGNORECASE
    )

    for i, line in enumerate(lines[:12]):
        if skip.search(line):
            continue

        # If a company suffix is on this line, join it
        # with the preceding line when appropriate.
        if company_suffix.search(line):
            if i > 0 and not skip.search(lines[i - 1]):
                return lines[i - 1] + " " + line
            return line

        # Otherwise use the first plausible company-name line
        if re.search(r"[A-Za-z]{3,}", line):
            if i + 1 < len(lines) and company_suffix.search(lines[i + 1]):
                return line + " " + lines[i + 1]
            return line

    return "Not found"

def extract_pdf_text(uploaded_file):
    text = ""

    with pymupdf.open(
        stream=uploaded_file.getvalue(),
        filetype="pdf"
    ) as pdf:
        for page in pdf:
            text += page.get_text() + "\n"

    return text


def extract_image_text(uploaded_file):
    image = Image.open(BytesIO(uploaded_file.getvalue()))
    return pytesseract.image_to_string(
    image,
    config="--psm 6"
)


uploaded_file = st.file_uploader(
    "Upload an invoice or receipt",
    type=["txt", "pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".txt"):
            text = uploaded_file.getvalue().decode(
                "utf-8", errors="replace"
            )
        elif filename.endswith(".pdf"):
            text = extract_pdf_text(uploaded_file)
        else:
            text = extract_image_text(uploaded_file)

        if not text.strip():
            st.warning(
                "No readable text found. Try a clearer image or PDF."
            )
            st.stop()

        invoice_number = extract_field(
            text, r"Invoice Number\s*[:=]+\s*(.+)"
        )
        date = extract_field(
    text,
    r"(?:Invoice\s+)?Date\s*[:=]?\s*([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4}|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})"
)
        vendor = extract_vendor(text)
        total = extract_field(
            text,
            r"Total Amount(?:\s*\(INR\))?\s*:?\s*([0-9,]+(?:\.[0-9]{1,2})?)"
        )

        st.success("Invoice text processed successfully!")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Vendor", vendor)
            st.metric("Invoice Number", invoice_number)

        with col2:
            st.metric("Total Amount", total)
            st.metric("Invoice Date", date)

        with st.expander("View extracted invoice text"):
            st.text(text)

    except Exception as error:
        st.error(f"Invoice processing failed: {error}")
