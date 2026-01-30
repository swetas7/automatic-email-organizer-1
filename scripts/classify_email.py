from transformers import pipeline
from scripts.fetch_email import gmail_authenticate, fetch_one_unread_email

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


def classify_email(text):
    print("Loading zero-shot classifier...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

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
    print("Authenticating Gmail...")
    service = gmail_authenticate()
    print("Fetching unread email...")
    email = fetch_one_unread_email(service)

    # THIS CHECK MUST BE IMMEDIATELY AFTER FETCH
    if not email:
        print("No unread emails found.")
        exit()

    print("\nEMAIL PREVIEW")
    print("FROM   :", email["from"])
    print("SUBJECT:", email["subject"])
    print("BODY   :", email["body"][:300])

    print("\nRunning AI classification...\n")

    label, score = classify_email(email["body"])

    print("AI CLASSIFICATION RESULT")
    print(f"Category   : {label}")
    print(f"Confidence : {round(score, 2)}")
    
    print("\nApplying Label to Gmail...")
    apply_label_to_email(service, email["id"], label)
