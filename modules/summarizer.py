import re
import spacy
from transformers import pipeline

# --- Load spaCy English model ---
nlp = spacy.load("en_core_web_sm")

# --- Load Hugging Face summarizers ---
study_notes_summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

# --- Helper functions ---
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_sections(text):
    """
    Split text into sections based on Unit / Topic / Problem Solving headings.
    """
    pattern = r"(Unit\s*-\s*\w+|Problem Solving|Topic:)"
    parts = re.split(pattern, text)
    sections = []
    i = 0
    while i < len(parts):
        if re.match(pattern, parts[i]):
            title = parts[i].strip()
            content = parts[i+1].strip() if i+1 < len(parts) else ""
            sections.append((title, content))
            i += 2
        else:
            i += 1
    return sections

def extract_keywords(text, top_n=10):
    """
    Extract key concepts from text using spaCy noun chunks + proper nouns.
    """
    doc = nlp(text)
    keywords = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text) > 2:
            keywords.add(chunk.text.strip())
    for token in doc:
        if token.pos_ in ["PROPN", "NOUN"] and len(token.text) > 2:
            keywords.add(token.text.strip())
    return list(keywords)[:top_n]

def find_sentence_for_keyword(text, keyword):
    """
    Return the most relevant sentence containing the keyword.
    """
    doc = nlp(text)
    for sent in doc.sents:
        if keyword.lower() in sent.text.lower():
            return clean_text(sent.text)
    return f"Definition of {keyword} not found."

# --- Main function ---
def summarize_text(text):
    text = clean_text(text)
    sections = extract_sections(text)
    
    quick_bullets = []
    study_notes = []
    exam_guide = []

    # Quick bullets = top 5-7 sentences (extractive)
    doc = nlp(text)
    sentence_scores = {}
    for sent in doc.sents:
        score = sum(2 if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"] else 1 for token in sent)
        sentence_scores[sent.text.strip()] = score
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    quick_bullets = sorted_sentences[:7]

    # Study Notes & Exam Guide
    for title, content in sections:
        if not content:
            continue

        # --- Study Notes ---
        summary = study_notes_summarizer(content, max_length=200, min_length=80, do_sample=False)[0]['summary_text']
        study_notes.append(f"📘 {title}\n{summary}\n")

        # --- Exam Guide / Keywords ---
        keywords = extract_keywords(content, top_n=15)
        for kw in keywords:
            sentence = find_sentence_for_keyword(content, kw)
            exam_guide.append(f"{kw}: {sentence}")

    return {
        "quick_bullets": quick_bullets,
        "study_notes": study_notes,
        "exam_guide": exam_guide
    }
