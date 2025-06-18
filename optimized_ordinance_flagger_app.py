
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai
import json

# Load OpenAI API Key
openai.api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("Enter your OpenAI API key:", type="password")

st.set_page_config(page_title="Solar Ordinance Risk Flagger", layout="centered")
st.title("📘 Solar Ordinance Risk Flagger")
st.markdown("Upload a full ordinance PDF to automatically flag key solar development risks categorized by permitting topics.")

uploaded_file = st.file_uploader("📄 Upload an ordinance PDF", type="pdf")

def extract_pdf_text(pdf_file):
    # Extracts text from all pages of a PDF document.
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def gpt_risk_analysis(text):
    # Calls GPT-4 to analyze text and return structured risk flags.
    prompt = f'''
You are a permitting analyst for solar EPC projects. Review the ordinance text and flag any risks across these categories:

1. Zoning Restrictions
2. Building Code Conflicts (e.g., underground conduit or CAB bans)
3. Stormwater or Environmental Constraints
4. Screening or Aesthetic Requirements
5. Permit Timeline Delays
6. Administrative or Legal Burdens

Output structured JSON in this format:
[
  {{
    "Category": "Zoning Restrictions",
    "Flagged Text": "...",
    "Page": 3,
    "Summary": "Example: This section prohibits solar in ag-zoned areas unless a CUP is approved."
  }}
]

Text:
"""{text}"""
'''
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You analyze legal texts for risks to solar permitting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )
    return response.choices[0].message.content

if uploaded_file and openai.api_key:
    with st.spinner("🔍 Analyzing ordinance for risk flags..."):
        try:
            ordinance_text = extract_pdf_text(uploaded_file)
            gpt_output = gpt_risk_analysis(ordinance_text)

            st.subheader("⚠️ Flagged Risk Sections")
            st.code(gpt_output, language="json")

            # Parse and display structured results
            risk_data = json.loads(gpt_output)
            df = pd.DataFrame(risk_data)
            st.dataframe(df)

            csv_data = df.to_csv(index=False)
            st.download_button("📥 Download Flagged Risks as CSV", data=csv_data, file_name="solar_risks.csv", mime="text/csv")

        except Exception as e:
            st.error(f"❌ Error processing document: {e}")
            if 'gpt_output' in locals():
                st.text(gpt_output)
