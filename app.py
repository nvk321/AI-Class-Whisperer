import os
import streamlit as st
from modules.pdf_utils import extract_text_from_pdf
from modules.summarizer import summarize_text

# Streamlit page setup
st.set_page_config(
    page_title="AI Class Whisperer",
    page_icon="🎓",
    layout="wide"
)

# --- Initialize session state for extracted text ---
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""

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

    if uploaded_file:
        # Ensure data folder exists
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Sanitize filename
        safe_filename = uploaded_file.name.replace(" ", "_")
        temp_path = os.path.join(data_dir, safe_filename)

        # Save uploaded PDF
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state["extracted_text"] = extract_text_from_pdf(temp_path)
        st.success("✅ PDF uploaded & text extracted successfully!")

    if input_text.strip():
        st.session_state["extracted_text"] = input_text
        st.success("✅ Text received!")

    if st.session_state["extracted_text"]:
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Preview:", st.session_state["extracted_text"], height=200)
# --- Summarizer Page ---
elif page == "📝 Summarizer":
    if st.session_state["extracted_text"]:
        summaries = summarize_text(st.session_state["extracted_text"])

        # --- Quick Bullets ---
        st.subheader("Quick Bullets (Revision)")
        for i, bullet in enumerate(summaries["quick_bullets"], 1):
            st.write(f"{i}. {bullet}")

        st.markdown("---")  # separator

        # --- Study Notes (Abstractive) ---
        st.subheader("Study Notes")
        for note in summaries["study_notes"]:
            # The heading is already included in the note from summarizer.py
            st.markdown(note)
            st.markdown("")  # small space between notes

        st.markdown("---")  # separator

        # --- Exam Guide (Key Concepts) ---
        st.subheader("Exam Guide (Key Concepts)")
        # Display as a clean bullet list instead of comma-separated
        for concept in summaries["exam_guide"]:
            st.write(f"- {concept}")

    else:
        st.warning("⚠️ Please upload a PDF or paste text in the 'PDF/Text Upload' section first.")

# --- Flashcards Page ---
elif page == "🧠 Flashcards":
    st.header("🧠 Flashcards & Quizzes")
    if st.session_state["extracted_text"]:
        st.info("Flashcards and quizzes will be generated here soon.")
    else:
        st.warning("⚠️ Please upload a PDF or paste text in the 'PDF/Text Upload' section first.")

# --- Analytics Page ---
elif page == "📊 Analytics (coming soon)":
    st.header("📊 Learning Analytics Dashboard")
    st.warning("🚧 Feature under development.")
