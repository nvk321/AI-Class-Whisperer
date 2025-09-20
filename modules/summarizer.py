import spacy
from transformers import pipeline
from collections import Counter
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Load HuggingFace summarization pipeline (explicit model)
SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"
summarizer = pipeline(
    "summarization",
    model=SUMMARIZATION_MODEL,
    tokenizer=SUMMARIZATION_MODEL,
    clean_up_tokenization_spaces=True
)

def summarize_text(text):
    """
    Returns 3 types of summaries:
    1. Quick Bullets – extractive, concise sentences
    2. Study Notes – abstractive, simplified notes
    3. Exam Guide – key concepts & terms
    """
    doc = nlp(text)
    sentences = list(doc.sents)

    # --- Quick Bullets (extractive) ---
    sentence_scores = {}
    for sent in sentences:
        score = 0
        for token in sent:
            if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"]:
                score += 2
            else:
                score += 1
        sentence_scores[sent.text] = score

    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    quick_bullets = [s for s in sorted_sentences[:5]]

    # --- Study Notes (abstractive) ---
    # Chunk text to avoid model input limits
    chunk_size = 1000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    study_notes = []

    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
            study_notes.append(summary)
        except Exception as e:
            study_notes.append("Error summarizing this chunk.")

    # Merge chunks into one coherent note
    study_notes = " ".join(study_notes)

    # --- Exam Guide (key concepts) ---
    exam_guide = set()
    for token in doc:
        if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"]:
            clean_token = re.sub(r'[^A-Za-z0-9]+', '', token.text)
            if clean_token:
                exam_guide.add(clean_token)

    return {
        "quick_bullets": quick_bullets,
        "study_notes": study_notes,
        "exam_guide": sorted(list(exam_guide))
    }
