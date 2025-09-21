# app.py
import os
import io
import json
import streamlit as st
from modules.pdf_utils import extract_text_from_pdf
from modules.summarizer import summarize_text
from modules.flashcards import generate_flashcards, generate_mcqs

st.set_page_config(page_title="AI Class Whisperer", page_icon="🎓", layout="wide")

# --- Session state init ---
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""
if "summaries" not in st.session_state:
    st.session_state["summaries"] = None
if "flashcards" not in st.session_state:
    st.session_state["flashcards"] = None
if "mcqs" not in st.session_state:
    st.session_state["mcqs"] = None

# --- Sidebar ---
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Choose a feature:",
    ["🏠 Home", "📄 PDF/Text Upload", "📝 Summarizer", "🧠 Flashcards & MCQs"]
)
st.sidebar.markdown("---")
st.sidebar.info("AI Class Whisperer – GenAI-powered learning assistant for students.")

# --- Home ---
if page == "🏠 Home":
    st.title("🎓 AI Class Whisperer")
    st.subheader("Your AI-powered study companion")
    st.markdown(
        """
        **Features**
        - 📄 PDF/Text Extraction
        - 📝 Multi-Level Summarization (Quick Bullets, Teacher-style study notes, Mini glossary)
        - 🧠 Flashcards & Auto MCQs (from provided text)
        
        Tip: Upload or paste course text on the "PDF/Text Upload" page, then go to "Summarizer".
        """
    )

# --- PDF/Text Upload ---
elif page == "📄 PDF/Text Upload":
    st.header("📄 Upload Course Material")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    input_text = st.text_area("Or paste your text here:", height=220)

    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        safe_filename = uploaded_file.name.replace(" ", "_")
        temp_path = os.path.join("data", safe_filename)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            st.session_state["extracted_text"] = extract_text_from_pdf(temp_path)
            st.success("✅ PDF uploaded & text extracted successfully!")
            # reset downstream caches
            st.session_state["summaries"] = None
            st.session_state["flashcards"] = None
            st.session_state["mcqs"] = None
        except Exception as e:
            st.error(f"Failed to extract PDF text: {e}")

    if input_text.strip():
        st.session_state["extracted_text"] = input_text
        st.success("✅ Text received!")
        st.session_state["summaries"] = None
        st.session_state["flashcards"] = None
        st.session_state["mcqs"] = None

    if st.session_state["extracted_text"]:
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Preview:", value=st.session_state["extracted_text"], height=250)

# --- Summarizer ---
elif page == "📝 Summarizer":
    st.header("📝 Summarizer")
    if not st.session_state["extracted_text"]:
        st.warning("⚠️ Upload a PDF or paste text first on the 'PDF/Text Upload' page.")
    else:
        # Controls
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Regenerate Summaries", key="regenerate_summaries"):
                st.session_state["summaries"] = None
        with col2:
            show_raw = st.checkbox("Show raw extracted text", key="show_raw_text")
        with col3:
            st.write("")  # placeholder for layout

        if show_raw:
            st.text_area("Raw extracted text", value=st.session_state["extracted_text"], height=180)

        # Generate summaries (cached via session_state)
        if not st.session_state["summaries"]:
            with st.spinner("Generating summaries (Quick Bullets, Study Notes, Mini-Glossary)..."):
                try:
                    st.session_state["summaries"] = summarize_text(st.session_state["extracted_text"])
                except Exception as e:
                    st.error(f"Summarization failed: {e}")
                    st.session_state["summaries"] = {"quick_bullets": [], "study_notes": [], "exam_guide": []}

        summaries = st.session_state["summaries"] or {"quick_bullets": [], "study_notes": [], "exam_guide": []}

        # Quick Bullets
        st.subheader("📌 Quick Bullets (Revision)")
        if summaries.get("quick_bullets"):
            for i, bullet in enumerate(summaries["quick_bullets"], 1):
                st.markdown(f"**{i}.** {bullet}")
        else:
            st.info("No quick bullets could be extracted.")

        st.markdown("---")

        # Study Notes
        st.subheader("📖 Study Notes (Teacher-style)")
        study_notes = summaries.get("study_notes", [])
        if study_notes:
            # show notes in an expander and provide download
            with st.expander("View full study notes (expand to copy)", expanded=True):
                full_notes_text = "\n\n".join(study_notes)
                st.text_area("Full Study Notes (copy or download below)", value=full_notes_text, height=320, key="full_notes_area")
                b = full_notes_text.encode("utf-8")
                st.download_button("Download Study Notes (.md)", data=b, file_name="study_notes.md", mime="text/markdown", key="download_study_notes")
            st.success("Study notes are ready. Use the text area or the download button to copy them.")
        else:
            st.info("No study notes produced for this text.")

        st.markdown("---")

        # Exam Guide (Mini-Glossary)
        st.subheader("📚 Exam Guide (Mini-Glossary)")
        exam_guide = summaries.get("exam_guide", [])
        if exam_guide:
            with st.expander("Click to view mini-glossary", expanded=False):
                for idx, line in enumerate(exam_guide, 1):
                    st.write(f"**{idx}.** {line}")
                # download glossary as text
                glossary_text = "\n".join(exam_guide)
                st.download_button("Download Mini-Glossary (.txt)", data=glossary_text.encode("utf-8"), file_name="mini_glossary.txt", mime="text/plain", key="download_glossary")
        else:
            st.info("No key concepts found. You can try 'Regenerate Summaries' with different input.")

# --- Flashcards & MCQs ---
elif page == "🧠 Flashcards & MCQs":
    st.header("🧠 Flashcards & MCQs")
    if not st.session_state["extracted_text"]:
        st.warning("⚠️ Upload a PDF or paste text first on the 'PDF/Text Upload' page.")
    else:
        # Generate / regenerate
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Generate Flashcards & MCQs", key="gen_flashcards"):
                st.session_state["flashcards"] = None
                st.session_state["mcqs"] = None
                with st.spinner("Generating flashcards & MCQs..."):
                    try:
                        st.session_state["flashcards"] = generate_flashcards(st.session_state["extracted_text"])
                        st.session_state["mcqs"] = generate_mcqs(st.session_state["extracted_text"])
                    except Exception as e:
                        st.error(f"Flashcard generation failed: {e}")
                        st.session_state["flashcards"] = []
                        st.session_state["mcqs"] = []
        with col2:
            if st.button("Clear Generated Cards", key="clear_flashcards"):
                st.session_state["flashcards"] = None
                st.session_state["mcqs"] = None

        # Display flashcards
        flashcards = st.session_state.get("flashcards")
        mcqs = st.session_state.get("mcqs")

        if flashcards:
            st.subheader("📇 Flashcards")
            flash_md_list = []
            for idx, card in enumerate(flashcards, 1):
                st.markdown(f"**Q{idx}:** {card.get('question')}")
                st.markdown(f"**A:** {card.get('answer')}")
                st.markdown("---")
                flash_md_list.append(f"Q{idx}: {card.get('question')}\nA: {card.get('answer')}\n")
            flash_all_text = "\n".join(flash_md_list)
            st.download_button("Download Flashcards (.md)", data=flash_all_text.encode("utf-8"), file_name="flashcards.md", mime="text/markdown", key="download_flashcards")

        if mcqs:
            st.subheader("❓ Multiple Choice Questions")
            mcq_md_list = []
            for idx, item in enumerate(mcqs, 1):
                st.markdown(f"**Q{idx}:** {item.get('question')}")
                options = item.get("options", [])
                for i, opt in enumerate(options, 1):
                    st.markdown(f"{i}. {opt}")
                st.markdown(f"**Answer:** {item.get('answer')}")
                st.markdown("---")
                # build md string
                opts_md = "\n".join([f"{i}. {o}" for i, o in enumerate(options, 1)])
                mcq_md_list.append(f"Q{idx}: {item.get('question')}\n{opts_md}\nAnswer: {item.get('answer')}\n")
            mcq_all_text = "\n".join(mcq_md_list)
            st.download_button("Download MCQs (.md)", data=mcq_all_text.encode("utf-8"), file_name="mcqs.md", mime="text/markdown", key="download_mcqs")

        if not flashcards and not mcqs:
            st.info("No flashcards / MCQs generated yet. Click 'Generate Flashcards & MCQs' to create them.")

# End of app
