import streamlit as st
from txtai.pipeline import Summary, Textractor
from PyPDF2 import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
import tempfile
import os
import google.generativeai as genai

# Set page configuration
st.set_page_config(layout="wide")

# Load environment variables
# Load your environment variables using dotenv if needed

# Configure Google API for audio summarization
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

prompt="""You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Function to summarize text using txtai
def text_summary(text):
    summary = Summary()
    result = summary(text)
    return result

# Function to extract text from a PDF document
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        text = page.extract_text()
    return text

# Function to extract transcript details from a YouTube video
def extract_transcript_details(youtube_video_url):
    video_id = youtube_video_url.split("=")[1]
    transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ""
    for i in transcript_text:
        transcript += " " + i["text"]
    return transcript

# Function to generate detailed notes from transcript text using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

    

# Function to summarize audio using Google's Generative AI
def summarize_audio(audio_file_path):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(["Please summarize the following audio.", audio_file])
    return response.text

# Function to save uploaded file to a temporary file and return the path
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None

# Sidebar with choices
choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document", "Summarize YouTube Video", "Summarize Audio"])

# Main content based on choice
# Main content based on choice
# Summarize Text
if choice == "Summarize Text":
    st.subheader("Summarize Text using txtai")
    input_text = st.text_area("Enter your text here")
    if input_text is not None:
        if st.button("Summarize Text"):
             col1, col2 = st.columns([1,1])
             with col1:
                st.markdown("**Your Input Text**")
                st.info(input_text)
             with col2:
                st.markdown("**Summary Result**")
                result = text_summary(input_text)
                st.success(result)


# Summarize Document
elif choice == "Summarize Document":
    st.subheader("Summarize Document using txtai")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    if input_file is not None:
        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                st.info("File uploaded successfully")
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                st.markdown("**Summary Result**")
                text = extract_text_from_pdf("doc_file.pdf")
                doc_summary = text_summary(text)
                st.success(doc_summary)
                
# Summarize YouTube Video
elif choice == "Summarize YouTube Video":
    st.subheader("Summarize YouTube Video using Google Gemini Pro")
    youtube_link = st.text_input("Enter YouTube Video Link:")
    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    if st.button("Get Detailed Notes"):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text,prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)

elif choice == "Summarize Audio":
    # Audio summarization logic
    st.subheader("Summarize Audio using Google's Generative AI")
    audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
    if audio_file is not None:
        audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
        st.audio(audio_path)

        if st.button('Summarize Audio'):
            with st.spinner('Summarizing...'):
                summary_text = summarize_audio(audio_path)
                st.info(summary_text)
