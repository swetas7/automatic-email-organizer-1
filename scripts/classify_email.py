from transformers import pipeline
from scripts.fetch_email import gmail_authenticate, fetch_one_unread_email
from scripts.summarize_email import summarize_email
from scripts.security_scan import scan_email

CATEGORIES = [
    "Classes & Lectures",
    "Exams & Academics",
    "Assignments & Deadlines",
    "Placements & Internships",
    "Club Activities",
    "Events & Workshops",
    "Competitions & Hackathons",
    "Administrative Notices",
    "Finance & Fees",
    "General Announcements",
    "Spam / Promotions"
]


# Cache the classifier globally
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("Loading zero-shot classifier (first time only)...")
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _classifier

def classify_email(text):
    # Check for empty text
    if not text or len(text.strip()) < 10:
        return "No Readable Text", 0.0
    
    classifier = get_classifier()
    result = classifier(text, CATEGORIES)
    return result["labels"][0], result["scores"][0]

def apply_label_to_email(service, msg_id, label_name):
    """Creates the label if not exists, and applies it to the email."""
    try:
        # 1. List existing labels to check if it exists
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        
        label_id = None
        for l in labels:
            if l["name"].lower() == label_name.lower():
                label_id = l["id"]
                break
        
        # 2. Create label if missing
        if not label_id:
            print(f"Creating new label: {label_name}")
            label_object = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
            created_label = service.users().labels().create(userId="me", body=label_object).execute()
            label_id = created_label["id"]
        
        # 3. Apply label to message
        body = {
            "addLabelIds": [label_id],
            "removeLabelIds": []
        }
        service.users().messages().modify(userId="me", id=msg_id, body=body).execute()
        print(f"Label '{label_name}' applied to message {msg_id}")
        return True

    except Exception as e:
        print(f"Error applying label: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("Authenticating Gmail...")
    service = gmail_authenticate()
    
    # Check if date argument provided
    date_filter = None
    if len(sys.argv) > 1:
        date_filter = sys.argv[1]
        print(f"Filtering by date: {date_filter}")
    
    print("Fetching emails...")
    from scripts.fetch_email import fetch_unread_emails
    emails = fetch_unread_emails(service, max_results=10, date_filter=date_filter)

    if not emails:
        print("No emails found.")
        exit()

    print(f"\n{'='*60}")
    print(f"Processing {len(emails)} emails...")
    print(f"{'='*60}")

    for i, email in enumerate(emails, 1):
        print(f"\n--- Email {i}/{len(emails)} ---")
        print(f"FROM   : {email['from']}")
        print(f"SUBJECT: {email['subject']}")
        
        label, score = classify_email(email["body"])
        
        print(f"CATEGORY: {label}")
        print(f"CONFIDENCE: {round(score, 2)}")
        
               # Generate summary
        summary = summarize_email(email["body"])
        print(f"SUMMARY: {summary}")
        
        # Security scan
        is_safe, security_reason = scan_email(email["subject"], email["body"], email["from"])
        if is_safe:
            print("SECURITY: ✅ Safe")
        else:
            print(f"SECURITY: ⚠️ WARNING - {security_reason}")
        
        apply_label_to_email(service, email["id"], label)
        print("✓ Label applied!")

    print(f"\n{'='*60}")
    print(f"Done! Processed {len(emails)} emails.")
    print(f"{'='*60}")
