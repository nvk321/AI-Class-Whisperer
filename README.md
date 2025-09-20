# AI Class Whisperer

AI Class Whisperer is a **GenAI-powered learning assistant** that transforms raw course materials into structured study assets.  
It helps students with **summaries, flashcards, quizzes, and an interactive tutor** powered by **RAG (Retrieval-Augmented Generation)**.

---

## Features
- **PDF/Text Extraction** (pypdf + OCR with Tesseract)
-  **Multi-Level Summarization** (Hugging Face + NLTK)
-  **Flashcards & Auto MCQs** (Bloom’s taxonomy)
- **Conversational Tutor Agent** (LangChain + FAISS/Chroma)
- **Learning Analytics Dashboard**

---

##  Tech Stack
- **GenAI & NLP:** Hugging Face Transformers (DistilBART, FLAN-T5), OpenAI API
- **Agentic AI:** LangChain Agents + FAISS/ChromaDB
- **Document AI:** pypdf, pytesseract, LayoutLMv3 (optional)
- **ML:** scikit-learn, spaCy, NLTK
- **Frontend:** Streamlit + Plotly
- **Deployment:** Streamlit Cloud (primary)
---

## Project Structure
AI-Class-Whisperer/
│── app.py
│── requirements.txt
│── README.md
│── .gitignore
│── modules/
│ ├── pdf_utils.py
│ ├── summarizer.py
│ ├── flashcards.py
│ ├── quiz_generator.py
│ ├── tutor_agent.py
│ ├── rag_utils.py
│ └── analytics.py
│ 
│── data/
│ └── vector_store/
│── assets/
│ └── sample_pdfs/

---

## Start Instructions
```bash
git clone https://github.com/nvk321/AI-Class-Whisperer.git
cd AI-Class-Whisperer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
---

## Status:

Under development