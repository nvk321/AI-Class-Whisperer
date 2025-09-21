import spacy
from collections import Counter
from transformers import pipeline

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Load HuggingFace summarization pipeline
summarizer = pipeline("summarization")

def clean_exam_tokens(tokens):
    """Remove short/broken tokens and duplicates."""
    cleaned = set()
    for token in tokens:
        t = token.strip()
        if len(t) > 2 and t.isalpha():
            cleaned.add(t)
    return sorted(cleaned)

def summarize_text(text):
    """
    Returns 3 types of summaries:
    1. Quick Bullets – extractive, concise sentences
    2. Study Notes – abstractive, simplified notes
    3. Exam Guide – key concepts & terms
    """
    doc = nlp(text)
    sentences = list(doc.sents)

    # --- Quick Bullets (extractive, full sentences) ---
    sentence_scores = {}
    for sent in sentences:
        score = 0
        for token in sent:
            if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"]:
                score += 2
            else:
                score += 1
        sentence_scores[sent.text.strip()] = score

    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    quick_bullets = sorted_sentences[:7]  # top 7 for better coverage

    # --- Study Notes (abstractive, student-friendly) ---
    # Split text by paragraphs instead of arbitrary chunk size
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    study_notes = []
    for idx, para in enumerate(paragraphs, 1):
        # Skip too short paragraphs
        if len(para.split()) < 20:
            continue
        summary = summarizer(para, max_length=180, min_length=60, do_sample=False)[0]['summary_text']
        # Use first noun chunk as heading if exists
        heading = list(nlp(para).noun_chunks)[0].text if list(nlp(para).noun_chunks) else f"Section {idx}"
        study_notes.append(f"**{heading}:** {summary}")

    # --- Exam Guide (key concepts) ---
    exam_tokens = [token.text for token in doc if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"]]
    exam_guide = clean_exam_tokens(exam_tokens)

    return {
        "quick_bullets": quick_bullets,
        "study_notes": study_notes,
        "exam_guide": exam_guide
    }
