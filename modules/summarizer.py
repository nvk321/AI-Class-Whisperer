# modules/summarizer.py
import re
import spacy
from transformers import pipeline

# --- Load spaCy (ensure en_core_web_sm is installed) ---
nlp = spacy.load("en_core_web_sm")

# --- Use a lighter abstractive summarizer for study notes ---
study_notes_summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

# --- Helper functions ---
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\.\s*){2,}', '. ', text)
    return text.strip()

def extract_sections(text: str):
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
    if not sections:
        return [("Document", text)]
    return sections

def extract_keywords(text: str, top_n: int = 8):
    doc = nlp(text)
    keywords = []
    seen = set()
    for token in doc:
        if token.is_alpha and token.pos_ in ("NOUN", "PROPN") and len(token.text) > 3:
            k = token.text.strip()
            kl = k.lower()
            if kl not in seen:
                keywords.append(k)
                seen.add(kl)
            if len(keywords) >= top_n:
                break
    return keywords

def find_sentence_for_keyword(text: str, keyword: str) -> str:
    """
    Extracts the most relevant sentence for a keyword.
    Chooses the sentence with highest keyword density (frequency / length).
    Truncates long sentences to ~25 words for mini-glossary readability.
    """
    doc = nlp(text)
    best_sent = None
    best_score = 0

    for sent in doc.sents:
        sent_text = sent.text.strip()
        count = sent_text.lower().count(keyword.lower())
        if count == 0:
            continue
        score = count / len(sent_text.split())
        if score > best_score:
            best_score = score
            best_sent = sent_text

    if not best_sent:
        return f"{keyword}: definition not found."

    words = best_sent.split()
    if len(words) > 25:
        best_sent = " ".join(words[:25]) + "..."

    return f"{keyword}: {best_sent}"

def generate_definition(keyword: str, content: str) -> str:
    return find_sentence_for_keyword(content, keyword)

def summarize_section(title: str, content: str) -> str:
    content = clean_text(content)
    if not content:
        return f"**{title}**\n(No content found.)"

    word_count = len(content.split())
    if word_count < 40:
        summary = content
    else:
        max_len = min(200, max(60, word_count // 2))
        min_len = min(60, max(20, word_count // 6))
        try:
            summary = study_notes_summarizer(
                content,
                max_length=max_len,
                min_length=min_len,
                do_sample=False
            )[0]["summary_text"]
        except Exception:
            doc = nlp(content)
            sents = list(doc.sents)[:2]
            summary = " ".join([s.text for s in sents]).strip()

    return f"**{title}**\n{clean_text(summary)}"

def summarize_text(text: str):
    text = clean_text(text)
    sections = extract_sections(text)

    # Quick Bullets (extractive)
    doc = nlp(text)
    sentence_scores = {}
    for sent in doc.sents:
        score = sum(2 if (token.ent_type_ or token.pos_ in ["PROPN", "NOUN"]) else 1 for token in sent)
        sentence_scores[sent.text.strip()] = score
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    quick_bullets = sorted_sentences[:7]

    # Study notes + exam guide
    study_notes = []
    exam_guide = []
    seen_keywords = set()

    for title, content in sections:
        if not content.strip():
            continue
        study_notes.append(summarize_section(title, content))
        keywords = extract_keywords(content, top_n=8)
        for kw in keywords:
            kl = kw.lower()
            if kl in seen_keywords:
                continue
            exam_guide.append(generate_definition(kw, content))
            seen_keywords.add(kl)

    return {
        "quick_bullets": quick_bullets,
        "study_notes": study_notes,
        "exam_guide": exam_guide
    }
