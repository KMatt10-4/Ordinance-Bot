
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai

# Load API key from Streamlit secrets or user input
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("Enter your OpenAI API key:", type="password")

st.title("📘 Solar Ordinance Risk Flagger")
st.write("Upload a full ordinance PDF and get flagged risk areas categorized by relevance to solar project development.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

def extract_all_text(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text_by_page = [page.get_text() for page in document]
    return text_by_page

def analyze_with_gpt(full_text):
    prompt = f"""
You are a permitting expert for solar EPC projects. Analyze the following ordinance text and flag any risks across these categories:
1. Zoning Restrictions
2. Building Code Conflicts (e.g., underground/CAB)
3. Stormwater or Environmental Constraints
4. Screening or Aesthetic Requirements
5. Permit Timeline Delays
6. Other Administrative or Legal Burdens

Return the output in this structured JSON format:
[
  {{
    "Category": "Zoning Restrictions",
    "Flagged Text": "...",
    "Page": 1,
    "Summary": "This section restricts solar in agricultural zones unless a CUP is obtained."
  }},
  ...
]

Ordinance Text:
"""
{full_text}
"""
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You analyze legal texts for risks to solar permitting."},
                  {"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000
    )
    return response.choices[0].message.content

if uploaded_file and openai.api_key:
    with st.spinner("Extracting text and analyzing..."):
        all_text = extract_all_text(uploaded_file)
        full_text = "\n".join(all_text)
        gpt_output = analyze_with_gpt(full_text)

    st.subheader("🔍 GPT-Flagged Risks")
    st.code(gpt_output, language="json")

    # Optional: if GPT returns JSON structure, parse it
    try:
        import json
        data = json.loads(gpt_output)
        df = pd.DataFrame(data)
        st.dataframe(df)

        csv = df.to_csv(index=False)
        st.download_button("📥 Download Flags as CSV", data=csv, file_name="solar_risks_flagged.csv", mime="text/csv")

    except Exception as e:
        st.warning("GPT output could not be parsed as structured data.")
        st.text(gpt_output)
