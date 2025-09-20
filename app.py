import streamlit as st

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

    if uploaded_file:
        st.success("✅ PDF uploaded successfully! (Extraction coming soon)")
    if input_text.strip():
        st.success("✅ Text received! (Processing coming soon)")

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
