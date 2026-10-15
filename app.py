
import re
import streamlit as st

st.set_page_config(
    page_title="BillWise AI",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 BillWise AI")
st.subheader("Intelligent Invoice & Expense Analyzer")

st.write("Upload an invoice to extract important details automatically.")

uploaded_file = st.file_uploader(
    "Upload an invoice or receipt",
    type=["txt", "pdf", "png", "jpg", "jpeg"]
)


def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else "Not found"


if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")

    if uploaded_file.name.lower().endswith(".txt"):
        text = uploaded_file.getvalue().decode(
            "utf-8", errors="replace"
        )

        invoice_number = extract_field(
            text, r"Invoice Number:\s*(.+)"
        )
        date = extract_field(text, r"Date:\s*(.+)")
        vendor = extract_field(text, r"Vendor:\s*(.+)")
        total = extract_field(
            text, r"Total Amount:\s*([0-9,]+(?:\.[0-9]{1,2})?)"
        )

        st.subheader("📋 Extracted Invoice Details")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Vendor", vendor)
            st.metric("Invoice Number", invoice_number)

        with col2:
            st.metric("Total Amount", total)
            st.metric("Invoice Date", date)

        with st.expander("View original invoice text"):
            st.text(text)

    else:
        st.info("PDF and image extraction will be added in a later step.")
