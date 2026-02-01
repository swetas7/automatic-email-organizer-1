from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st

summarizer_model = None
summarizer_tokenizer = None

@st.cache_resource
def load_summarizer():
    print("🧠 Loading summarization model (cached)...")
    model_name = "sshleifer/distilbart-cnn-12-6"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

def summarize_email(text):
    """Generates a short summary of the email body."""
    try:
        if not text or len(text.strip()) < 50:
            return "Content too short to summarize."

        model, tokenizer = load_summarizer()
        
        # Truncate input to avoid token limits
        input_text = text[:1024]
        
        # Tokenize and generate
        inputs = tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs["input_ids"], max_length=60, min_length=15, num_beams=4)
        summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        return summary_text
        
    except Exception as e:
        print(f"Error summarizing: {e}")
        return "Could not generate summary."
