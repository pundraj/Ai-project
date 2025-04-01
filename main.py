import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import re

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Try direct text extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    # Fallback to OCR for image-based PDFs
    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip()

# Function to calculate ATS score
def calculate_ats_score(resume_text, job_description):
    if not resume_text or not job_description:
        return 0

    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    job_desc_words = set(re.findall(r'\b\w+\b', job_description.lower()))

    matched_keywords = resume_words.intersection(job_desc_words)
    ats_score = (len(matched_keywords) / len(job_desc_words)) * 100 if job_desc_words else 0

    return round(ats_score, 2)

# Function to get response from Gemini AI
# Modify the analyze_resume function
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}

    model = genai.GenerativeModel("gemini-1.5-flash")
    
    base_prompt = f"""
    Act as an expert Resume Critique Bot with extensive experience in professional resume writing and HR. Analyze the provided resume and provide detailed feedback in the following structured format:

    1. OVERALL IMPRESSION:
    - Provide a brief overview of the resume's effectiveness
    - Comment on the resume's organization and clarity

    2. CONTENT ANALYSIS:
    - Professional Experience
    - Education
    - Skills and Competencies
    - Achievements and Impact
    - Technical Proficiency

    3. FORMATTING AND PRESENTATION:
    - Layout and Design
    - Use of Action Verbs
    - Consistency
    - Professional Tone

    4. SPECIFIC RECOMMENDATIONS:
    - List 3-5 concrete improvements
    - Suggest better ways to phrase key experiences
    - Recommend additional sections if needed

    5. INDUSTRY ALIGNMENT:
    - Evaluate market readiness
    - Suggest industry-specific optimizations

    6. SKILL ENHANCEMENT:
    - Recommend relevant certifications
    - Suggest courses for skill development
    - Identify trending skills in the field

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        7. JOB MATCH ANALYSIS:
        - Compare resume against job requirements
        - Identify missing key qualifications
        - Suggest tailoring strategies

        Job Description:
        {job_description}
        """

    response = model.generate_content(base_prompt)
    return response.text.strip()

# After the imports, add the consolidated CSS
# In the CUSTOM_STYLES, update the .stApp class
CUSTOM_STYLES = """
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1557264337-e8a93017fe92?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        background-size: 100% 100%;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
        width: 100%;
        max-width: 100%;
        overflow-x: hidden;
    }
    .stMarkdown {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        background: none !important;
        padding: 0 !important;
    }
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid white;
        backdrop-filter: blur(5px);
    }
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
    }
    .stUploader {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    .stTab {
        color: white;
        background-color: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(5px);
    }
    .stTitle {
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stToolbar"] {
        display: none;
    }
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px);
        color: white !important;
    }
    .analysis-text {
        font-size: 18px !important;
        line-height: 1.8 !important;
        letter-spacing: 0.3px !important;
        color: white !important;
    }
    .analysis-text h1 {
        font-size: 24px !important;
        margin-bottom: 20px !important;
    }
    .analysis-text ul {
        margin-left: 20px !important;
        margin-bottom: 15px !important;
    }
    .ats-score {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    .content-box {
        border: 3px solid #8a2be2;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        background-color: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
    }
    </style>
"""

# Apply styles once at the start
st.markdown(CUSTOM_STYLES, unsafe_allow_html=True)

# Update the title and description
st.title("AI Resume Critique Bot")
st.write("Get detailed professional feedback on your resume from our AI-powered critique bot")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

if uploaded_file is not None:
    st.success("Resume uploaded successfully!")
else:
    st.warning("Please upload a resume in PDF format.")

st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)

if uploaded_file:
    # Save uploaded file locally for processing
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text from PDF
    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    # Update the success message
    # In the analyze button section, remove the duplicate CSS and just use the content HTML:
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing your resume..."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                ats_score = calculate_ats_score(resume_text, job_description)
                
                st.success("Resume Analysis Complete!")
                tab1, tab2 = st.tabs(["Detailed Analysis", "ATS Score"])
                
                with tab1:
                    st.markdown(f'<div class="content-box"><div class="analysis-text">{analysis}</div></div>', 
                              unsafe_allow_html=True)
                
                with tab2:
                    content = f"""
                    <div class="content-box">
                        <div class="analysis-text">
                            <h2>ATS Compatibility Score</h2>
                            {f'<p class="ats-score">🔹 ATS Score: {ats_score}%</p>' if job_description else '<p>Please provide a job description to calculate ATS score</p>'}
                            {
                                f'<div class="{"success" if ats_score > 80 else "warning" if ats_score > 50 else "error"}">'
                                f'{"Excellent ATS Optimization!" if ats_score > 80 else "Room for ATS Optimization" if ats_score > 50 else "Needs significant ATS optimization"}'
                                '</div>' if job_description else ''
                            }
                    </div>
                    """
                    st.markdown(content, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

# Footer
st.markdown("---")
st.markdown(
    """<p style='text-align: center;'>Powered by <b>Google Gemini AI</b> | Developed by 
    <b>Raj:12313983 | Aniket:12326195 | Subhadeep:12319137</b></p>""",
    unsafe_allow_html=True
)
