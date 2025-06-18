
import streamlit as st
import fitz  # PyMuPDF
import json
import re
import pandas as pd
from collections import defaultdict
import openai

# Function to extract text from PDF and chunk it by section
def extract_text_by_section(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    sections = re.split(r'\n\d+\.\s', text)
    return sections

# Function to validate and clean JSON output from GPT
def validate_and_clean_json(gpt_output):
    try:
        data = json.loads(gpt_output)
        return data
    except json.JSONDecodeError:
        # Attempt to clean and re-parse
        gpt_output = re.sub(r'(?<!\")(\\b\\w+\\b)(?!\")', r'\"\\1\"', gpt_output)
        data = json.loads(gpt_output)
        return data

# Function to perform keyword-based fallback analysis
def keyword_based_analysis(text, keywords):
    results = defaultdict(list)
    for keyword in keywords:
        if keyword.lower() in text.lower():
            results[keyword].append(text)
    return results

# Function to analyze text using GPT
def analyze_text_with_gpt(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Analyze the following text and return flagged sections in JSON format: {text}",
        max_tokens=500
    )
    gpt_output = response.choices[0].text.strip()
    return gpt_output

# Streamlit app
st.title("Ordinance Flagging App")

uploaded_file = st.file_uploader("Upload an ordinance PDF", type="pdf")

if uploaded_file is not None:
    st.spinner("Processing...")
    sections = extract_text_by_section(uploaded_file)
    flagged_results = defaultdict(list)
    
    for section in sections:
        try:
            gpt_output = analyze_text_with_gpt(section)
            validated_data = validate_and_clean_json(gpt_output)
            for category, items in validated_data.items():
                flagged_results[category].extend(items)
        except Exception as e:
            st.warning(f"GPT analysis failed: {e}")
            keywords = ["permit", "CAB", "noise", "decommissioning", "soil", "screening", "review", "AHJ"]
            keyword_results = keyword_based_analysis(section, keywords)
            for keyword, items in keyword_results.items():
                flagged_results[keyword].extend(items)
    
    st.success("Analysis complete!")
    
    # Display results
    for category, items in flagged_results.items():
        st.subheader(category)
        for item in items:
            st.write(item)
    
    # Downloadable CSV
    df = pd.DataFrame([(cat, item) for cat, items in flagged_results.items() for item in items], columns=["Category", "Flagged Text"])
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "flagged_results.csv", "text/csv")
    