
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# Define the risk categories and keywords
risk_categories = {
    "Zoning Regulations": [
        "agricultural zone", "residential zone", "setback", "height limitation", "CUP", "SUP", "noise", "glare", "visual impact", "monthly review"
    ],
    "Building Codes": [
        "underground conduit", "CAB", "structural code", "racking", "fencing", "height limitation", "engineering inspection", "3rd party review"
    ],
    "Environmental/Stormwater": [
        "impervious surface", "detention pond", "soil boring", "geotech study", "drainage report", "erosion control", "vegetation restoration"
    ],
    "Signage/Screening/Landscaping": [
        "berms", "landscape screening", "buffer zone", "emergency signage", "public signage", "visual screening"
    ],
    "Other Local Statutes": [
        "decommissioning plan", "surety bond", "fire safety", "access lane", "utility interconnection", "permit timeline", "host community agreement"
    ],
    "Access Permitting & AHJ": [
        "access permitting", "AHJ", "Authority Having Jurisdiction", "zoning", "building", "fire safety", "environmental compliance"
    ]
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(pdf_file) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to flag risks in the text
def flag_risks(text):
    flagged_sections = []
    for category, keywords in risk_categories.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                flagged_sections.append((category, keyword))
    return flagged_sections

# Streamlit app
st.title("Ordinance Risk Flagging App")

uploaded_file = st.file_uploader("Upload an Ordinance PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract text from the uploaded PDF
    text = extract_text_from_pdf(uploaded_file)

    # Flag risks in the extracted text
    flagged_sections = flag_risks(text)

    # Display flagged sections
    if flagged_sections:
        st.subheader("Flagged Sections")
        df = pd.DataFrame(flagged_sections, columns=["Category", "Keyword"])
        st.dataframe(df)

        # Download flagged sections as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Flagged Sections as CSV",
            data=csv,
            file_name="flagged_sections.csv",
            mime="text/csv",
        )
    else:
        st.write("No risks flagged in the uploaded document.")
