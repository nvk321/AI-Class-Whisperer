import os
import streamlit as st
from modules.pdf_utils import extract_text_from_pdf
from modules.summarizer import summarize_text, summarize_section
import pyperclip

st.set_page_config(page_title="AI Class Whisperer", page_icon="🎓", layout="wide")

# Session state
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""
if "summaries" not in st.session_state:
    st.session_state["summaries"] = None

# Sidebar
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Choose a feature:", ["🏠 Home", "📄 PDF/Text Upload", "📝 Summarizer", "🧠 Flashcards"])
st.sidebar.markdown("---")
st.sidebar.info("AI Class Whisperer – GenAI-powered learning assistant for students.")

# Home
if page == "🏠 Home":
    st.title("🎓 AI Class Whisperer")
    st.subheader("Your AI-powered study companion")
    st.markdown("""
    - 📄 Upload & process course PDFs
    - 📝 Generate concise & detailed summaries
    - 🧠 Create flashcards and quizzes
    """)

# PDF/Text Upload
elif page == "📄 PDF/Text Upload":
    st.header("📄 Upload Course Material")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    input_text = st.text_area("Or paste your text here:")

    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        safe_filename = uploaded_file.name.replace(" ", "_")
        temp_path = os.path.join("data", safe_filename)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["extracted_text"] = extract_text_from_pdf(temp_path)
        st.success("✅ PDF uploaded & text extracted!")

    if input_text.strip():
        st.session_state["extracted_text"] = input_text
        st.success("✅ Text received!")

    if st.session_state["extracted_text"]:
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Preview:", st.session_state["extracted_text"], height=200)

# Summarizer
elif page == "📝 Summarizer":
    st.header("📝 Summarizer")
    if st.session_state["extracted_text"]:
        if not st.session_state["summaries"]:
            with st.spinner("Generating summaries..."):
                st.session_state["summaries"] = summarize_text(st.session_state["extracted_text"])
        summaries = st.session_state["summaries"]

        # Quick Bullets
        st.subheader("Quick Bullets (Revision)")
        for i, bullet in enumerate(summaries["quick_bullets"], 1):
            st.markdown(f"{i}. {bullet}")
        st.markdown("---")

        # Study Notes
        st.subheader("Study Notes (Teacher-style)")
        full_notes = ""
        for title, content in summaries["section_summaries"]:
            full_notes += summarize_section(title, content) + "\n\n"
        st.markdown(full_notes)

        # Single copy button
        if st.button("Copy Full Study Notes"):
            pyperclip.copy(full_notes)
            st.success("✅ Study Notes copied to clipboard!")

        st.markdown("---")

        # Exam Guide
        st.subheader("Exam Guide (Mini-Glossary)")
        if summaries["exam_guide"]:
            with st.expander("Click to view glossary"):
                for idx, concept in enumerate(summaries["exam_guide"], 1):
                    st.write(f"{idx}. {concept}")
        else:
            st.info("No key concepts found.")
    else:
        st.warning("⚠️ Upload a PDF or paste text first.")

# Flashcards
elif page == "🧠 Flashcards":
    st.header("🧠 Flashcards & Quizzes")
    if st.session_state["extracted_text"]:
        st.info("Flashcards coming soon.")
    else:
        st.warning("⚠️ Upload a PDF or paste text first.")
