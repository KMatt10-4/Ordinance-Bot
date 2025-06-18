
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# Define risk categories and keywords
risk_categories = {
    "Permit Timeline Constraints": ["permit expiration", "permit timeline", "appeals process"],
    "CAB/Underground Electrical Restrictions": ["underground utilities", "subsurface drainage"],
    "Noise Setback Requirements": ["noise setback"],
    "Decommissioning Requirements": ["decommissioning", "long-term maintenance"],
    "Soil/Geo Studies": ["geotechnical review", "soil study", "boring"],
    "Visual Screening (Berms, Fences)": ["buffer requirements", "vegetated screening"],
    "Monthly Review Schedules": ["monthly review", "hearing timelines"],
    "3rd Party Engineering Review Triggers": ["engineering review", "professional engineer"],
    "Host Community Agreement Clauses": ["community agreement", "HOA obligations"],
    "Access Permitting & AHJ": ["access permitting", "authority having jurisdiction"]
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to flag sections based on keywords
def flag_sections(text, risk_categories):
    flagged_sections = []
    lines = text.split('
')
    for i, line in enumerate(lines):
        for category, keywords in risk_categories.items():
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    section_title = lines[i-1] if i > 0 else "Unknown Section"
                    page_number = (i // 50) + 1  # Estimate page number
                    flagged_sections.append({
                        "Category": category,
                        "Section Title": section_title,
                        "Summary": line,
                        "Page Number": page_number,
                        "Full Text": "
".join(lines[max(0, i-5):min(len(lines), i+5)])
                    })
    return flagged_sections

# Streamlit app
st.title("Ordinance Flagging App")
st.write("Upload an ordinance PDF to flag relevant sections for development and construction teams.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    flagged_sections = flag_sections(text, risk_categories)
    
    st.write("Flagged Sections:")
    for section in flagged_sections:
        st.write(f"**Category:** {section['Category']}")
        st.write(f"**Section Title:** {section['Section Title']}")
        st.write(f"**Summary:** {section['Summary']}")
        st.write(f"**Page Number:** {section['Page Number']}")
        st.write(f"**Full Text:** {section['Full Text']}")
        st.write("---")
    
    # Create a DataFrame for download
    df = pd.DataFrame(flagged_sections)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="Download Flagged Sections as CSV",
        data=csv,
        file_name="flagged_sections.csv",
        mime="text/csv"
    )
