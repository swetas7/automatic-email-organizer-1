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
    print("🧠 Loading zero-shot classifier...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

    result = classifier(text, CATEGORIES)

    return result["labels"][0], result["scores"][0]


if __name__ == "__main__":
    print("🔐 Authenticating Gmail...")
    service = gmail_authenticate()
print("📧 Fetching unread email...")
email = fetch_one_unread_email(service)

# THIS CHECK MUST BE IMMEDIATELY AFTER FETCH
if not email:
    print("❌ No unread emails found.")
    exit()

print("\n📨 EMAIL PREVIEW")
print("FROM   :", email["from"])
print("SUBJECT:", email["subject"])
print("BODY   :", email["body"][:300])

print("\n⚙️ Running AI classification...\n")

label, score = classify_email(email["body"])

print("✅ AI CLASSIFICATION RESULT")
print(f"Category   : {label}")
print(f"Confidence : {round(score, 2)}")
