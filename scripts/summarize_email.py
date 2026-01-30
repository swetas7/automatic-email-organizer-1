from transformers import pipeline

summarizer = None

def load_summarizer():
    global summarizer
    if summarizer is None:
        print("🧠 Loading summarization model...")
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return summarizer

def summarize_email(text):
    """Generates a short summary of the email body."""
    try:
        if not text or len(text.strip()) < 50:
            return "Content too short to summarize."

        model = load_summarizer()
        
        # Truncate input to avoid model token limits (approx check)
        input_text = text[:3000]
        
        # Generate summary (max 60 words, min 10 words)
        summary_list = model(input_text, max_length=60, min_length=15, do_sample=False)
        summary_text = summary_list[0]['summary_text']
        return summary_text
        
    except Exception as e:
        print(f"Error summarizing: {e}")
        return "Could not generate summary."
