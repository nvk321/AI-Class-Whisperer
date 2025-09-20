import streamlit as st
from modules.pdf_utils import extract_text_from_pdf

# Streamlit page setup
st.set_page_config(
    page_title="AI Class Whisperer",
    page_icon="🎓",
    layout="wide"
)

# --- Sidebar ---
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Choose a feature:",
    ["🏠 Home", "📄 PDF/Text Upload", "📝 Summarizer", "🧠 Flashcards", "📊 Analytics (coming soon)"]
)

st.sidebar.markdown("---")
st.sidebar.info("AI Class Whisperer – GenAI-powered learning assistant for students.")

# --- Home Page ---
if page == "🏠 Home":
    st.title("🎓 AI Class Whisperer")
    st.subheader("Your AI-powered study companion")
    st.markdown("""
    Welcome to **AI Class Whisperer** – an intelligent assistant that helps you:
    - 📄 Upload & process course PDFs
    - 📝 Get concise & detailed summaries
    - 🧠 Generate flashcards and quizzes
    - 💬 Interact with a tutor agent (coming soon)
    - 📊 Track learning progress (coming soon)

    🚀 Let's get started by uploading a PDF or pasting text!
    """)

# --- PDF/Text Upload Page ---
elif page == "📄 PDF/Text Upload":
    st.header("📄 Upload Course Material")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    input_text = st.text_area("Or paste your text here:")

    extracted_text = ""

    if uploaded_file:
        # Save temporary file
        temp_path = os.path.join("data", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        extracted_text = extract_text_from_pdf(temp_path)
        st.success("✅ PDF uploaded & text extracted successfully!")
    
    if input_text.strip():
        extracted_text = input_text
        st.success("✅ Text received!")

    if extracted_text:
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Preview:", extracted_text, height=200)
# --- Summarizer Page ---
elif page == "📝 Summarizer":
    st.header("📝 AI Summarizer")
    st.info("Upload text in the 'PDF/Text Upload' section first.")
    st.markdown("✨ Summaries (Quick Bullets, Study Notes, Exam Guide) will appear here soon.")

# --- Flashcards Page ---
elif page == "🧠 Flashcards":
    st.header("🧠 Flashcards & Quizzes")
    st.info("Upload text in the 'PDF/Text Upload' section first.")
    st.markdown("✨ Flashcards and quizzes will be generated here soon.")

# --- Analytics Page ---
elif page == "📊 Analytics (coming soon)":
    st.header("📊 Learning Analytics Dashboard")
    st.warning("🚧 Feature under development.")
