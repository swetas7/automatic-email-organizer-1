from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

summarizer_model = None
summarizer_tokenizer = None

def load_summarizer():
    global summarizer_model, summarizer_tokenizer
    if summarizer_model is None:
        print("🧠 Loading summarization model...")
        model_name = "sshleifer/distilbart-cnn-12-6"
        summarizer_tokenizer = AutoTokenizer.from_pretrained(model_name)
        summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return summarizer_model, summarizer_tokenizer

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
