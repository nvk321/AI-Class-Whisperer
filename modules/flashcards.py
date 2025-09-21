# modules/flashcards.py
import re
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
import random

# --- Load spaCy for keyword extraction ---
nlp = spacy.load("en_core_web_sm")

# --- Load T5 for question generation ---
tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-hl")
model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-hl")

# --- Helpers ---
def clean_text(text: str) -> str:
    """Clean whitespace and repeated characters"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text: str, top_n=10):
    """Return top N nouns/proper nouns as keywords"""
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

def generate_question(sentence: str):
    """Generate a meaningful question using T5"""
    sentence = clean_text(sentence)
    input_text = f"generate question: {sentence}"
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=64)
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return question

def generate_flashcards(text: str, max_flashcards=8):
    """Generate flashcards from the input text"""
    text = clean_text(text)
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    flashcards = []

    for i, sent in enumerate(sentences[:max_flashcards]):
        question = generate_question(sent)
        flashcards.append({"question": question, "answer": sent})

    return flashcards

def generate_mcqs(text: str, max_mcqs=8):
    """Generate MCQs with 1 correct and 3 distractors"""
    text = clean_text(text)
    keywords = extract_keywords(text, top_n=15)
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    mcqs = []

    for i, sent in enumerate(sentences[:max_mcqs]):
        # Correct answer
        answer = sent
        # Pick 3 random distractors from other sentences or keywords
        distractors = []
        tries = 0
        while len(distractors) < 3 and tries < 20:
            choice = random.choice(sentences + keywords)
            if choice != answer and choice not in distractors:
                distractors.append(choice)
            tries += 1
        # Shuffle options
        options = distractors + [answer]
        random.shuffle(options)
        mcqs.append({"question": generate_question(sent), "options": options, "answer": answer})

    return mcqs
