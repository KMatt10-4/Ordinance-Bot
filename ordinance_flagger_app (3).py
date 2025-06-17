
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# Function to extract text from PDF
def extract_text_from_first_page(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    first_page = document.load_page(0)
    text = first_page.get_text("text")
    return text

# Function to flag relevant sections based on keywords
def flag_sections(text, keywords):
    flagged_sections = []
    for keyword in keywords:
        if keyword.lower() in text.lower():
            flagged_sections.append(keyword)
    return flagged_sections

# Define keywords for flagging
keywords = [
    "zoning", "setback", "height limitation", "CUP", "SUP", "noise", "glare", "visual impact",
    "underground electrical", "CAB", "structural code", "racking", "fencing", "impervious surface",
    "soil boring", "geotech study", "drainage report", "vegetation", "erosion control", "berms",
    "landscape screening", "buffer zones", "signage", "decommissioning", "fire safety", "access lane",
    "utility interconnection", "permit timeline", "engineering review", "host community agreement",
    "access permitting", "AHJ"
]

# Streamlit app
st.title("Ordinance Flagging Bot")
st.write("Upload an ordinance PDF to flag relevant sections for development and construction teams.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from the first page of the PDF
    text = extract_text_from_first_page(uploaded_file)
    
    # Flag relevant sections
    flagged_sections = flag_sections(text, keywords)
    
    # Display flagged sections
    if flagged_sections:
        st.write("Flagged Sections:")
        for section in flagged_sections:
            st.write(f"- {section}")
    else:
        st.write("No relevant sections flagged.")
    
    # Generate and download report
    report_data = {"Flagged Sections": flagged_sections}
    report_df = pd.DataFrame(report_data)
    st.download_button(
        label="Download Report",
        data=report_df.to_csv(index=False),
        file_name="flagged_sections_report.csv",
        mime="text/csv"
    )
