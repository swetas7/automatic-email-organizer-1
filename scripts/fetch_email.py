import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def gmail_authenticate():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "auth/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def parse_message(service, msg_id):
    """Helper to fetch and parse a single message details."""
    try:
        msg = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        headers = msg["payload"]["headers"]
        subject = sender = "Unknown"

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        body = ""
        payload = msg["payload"]

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            data = payload["body"].get("data")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")
        
        return {
            "id": msg_id,
            "from": sender,
            "subject": subject,
            "body": body
        }
    except Exception as e:
        print(f"Error parsing message {msg_id}: {e}")
        return None

def fetch_unread_emails(service, max_results=10):
    """Fetches a list of unread emails."""
    print(f"Fetching up to {max_results} unread emails...")
    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    print(f"Found {len(messages)} unread messages.")
    
    email_data_list = []
    
    for message in messages:
        msg_id = message["id"]
        data = parse_message(service, msg_id)
        if data:
            email_data_list.append(data)

    return email_data_list

# Keep strict backward compatibility if needed, but we are updating app.py anyway
def fetch_one_unread_email(service):
    emails = fetch_unread_emails(service, max_results=1)
    if emails:
        return emails[0]
    return None

def fetch_demo_emails():
    """Returns fake emails for testing without credentials."""
    import datetime
    return [
        {
            "id": "mock_1",
            "from": "Prof. Smith <smith@university.edu>",
            "subject": "Final Exam Schedule - Dec 2026",
            "body": "Dear Students, The final exams will start from 15th Dec. Please check the attached schedule. Best, Prof. Smith"
        },
        {
            "id": "mock_2",
            "from": "Amazon <orders@amazon.com>",
            "subject": "Your package has been delivered",
            "body": "Hi Sresth, your package containing 'Gaming Mouse' was delivered today at 2:00 PM."
        },
        {
            "id": "mock_3",
            "from": "HDFC Bank <alerts@hdfc.com>",
            "subject": "Credit Card Bill Payment Reminder",
            "body": "Dear Customer, your bill of Rs. 15,000 is due on 5th Feb. Please pay to avoid late fees."
        },
        {
            "id": "mock_4",
            "from": "HR Team <hr@techcorp.com>",
            "subject": "Internship Offer Letter",
            "body": "Dear Candidate, We are pleased to offer you the internship position at TechCorp. Please sign by tomorrow."
        },
        {
            "id": "mock_5",
            "from": "Eventbrite <noreply@eventbrite.com>",
            "subject": "You are registered: Hackathon 2026",
            "body": "You are confirmed for the event. Venue: Main Auditorium. Time: 9:00 AM."
        },
        {
            "id": "mock_6",
            "from": "Security Alert <admin@secure-login-verify.com>",
            "subject": "URGENT: Verify Password Immediately",
            "body": "Dear User, We detected unauthorized access. Click here to unlock your account or it will be suspended. Verify your account now."
        },
        {
            "id": "mock_7",
            "from": "Weekly Digest <newsletter@techplanet.com>",
            "subject": "Top Tech News of the Week",
            "body": "Hi Sresth, Here is your weekly round up of tech news. View in browser. If you wish to opt out, you can unsubscribe here."
        },
        {
            "id": "mock_8",
            "from": "Marketing Team <promo@shop-now.com>",
            "subject": "Huge Sale! 50% Off Everything",
            "body": "Don't miss out on our biggest sale of the year. Terms of use apply. Unsubscribe from this list."
        }
    ]
