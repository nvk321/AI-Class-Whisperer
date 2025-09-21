import re
import spacy
from transformers import pipeline

# --- Load spaCy ---
nlp = spacy.load("en_core_web_sm")

# --- Hugging Face Summarizer ---
study_notes_summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# --- Helper functions ---
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\.\s*){2,}', '. ', text)
    return text.strip()

def extract_sections(text):
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
    doc = nlp(text)
    for sent in doc.sents:
        if keyword.lower() in sent.text.lower():
            return clean_text(sent.text)
    return f"Definition of {keyword} not found."

def summarize_section(title, content):
    content = clean_text(content)
    # Split content into paragraphs for better summarization
    paragraphs = [p.strip() for p in re.split(r'\n+', content) if len(p.strip()) > 20]
    summary_list = []
    for para in paragraphs:
        summary = study_notes_summarizer(
            para,
            max_length=min(300, len(para.split())*2),
            min_length=min(80, len(para.split())),
            do_sample=False
        )[0]['summary_text']
        summary_list.append(clean_text(summary))
    return f"**{title}**\n" + "\n\n".join(summary_list)

def summarize_text(text):
    text = clean_text(text)
    sections = extract_sections(text)

    # --- Quick Bullets ---
    doc = nlp(text)
    sentence_scores = {}
    for sent in doc.sents:
        score = sum(2 if token.ent_type_ or token.pos_ in ["PROPN", "NOUN"] else 1 for token in sent)
        sentence_scores[sent.text.strip()] = score
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    quick_bullets = sorted_sentences[:7]

    # --- Study Notes & Exam Guide ---
    section_summaries = []
    exam_guide = []
    all_keywords = set()

    for title, content in sections:
        if not content.strip():
            continue
        section_summaries.append((title, content))
        keywords = extract_keywords(content, top_n=10)
        for kw in keywords:
            if kw.lower() not in all_keywords:
                sentence = find_sentence_for_keyword(content, kw)
                exam_guide.append(f"{kw}: {sentence}")
                all_keywords.add(kw.lower())

    return {
        "quick_bullets": quick_bullets,
        "section_summaries": section_summaries,
        "exam_guide": exam_guide
    }
