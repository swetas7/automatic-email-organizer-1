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

def fetch_one_unread_email(service):
    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=1
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return None

    msg_id = messages[0]["id"]

    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg["payload"]["headers"]
    subject = sender = ""

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
                body = base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode("utf-8")
    else:
        body = base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8")

    # ✅ RETURN DATA (NO PRINTING HERE)
    return {
        "id": msg_id,
        "from": sender,
        "subject": subject,
        "body": body
    }
