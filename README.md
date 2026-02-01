# Automatic Email Organizer

An AI-powered email management system that automatically classifies, summarizes, secures, and organizes Gmail inboxes, helping users focus on important communication.

---

## Features

| Feature | Description |
|-------|-------------|
| Auto Classification | Automatically categorizes emails (Academics, Placements, Events, etc.) |
| Smart Summarization | Generates concise summaries of long emails |
| Security Scanning | Detects phishing and suspicious emails |
| Newsletter Detection | Identifies promotional and newsletter emails |
| Reply Suggestions | AI-generated reply drafts |
| Gmail Labels | Automatically applies labels directly in Gmail |

---

## How It Works

1. User authenticates using Gmail OAuth 2.0  
2. Emails are fetched using the Gmail API  
3. AI models analyze email content  
4. Emails are classified into predefined categories  
5. Long emails are summarized automatically  
6. Suspicious or phishing emails are flagged  
7. Gmail labels are applied automatically  
8. All processed data is stored locally using SQLite  

---

## Tech Stack

- Frontend: Streamlit, Altair  
- Backend: Python, SQLite  
- AI Models: Hugging Face Transformers (BART)  
- APIs: Gmail API, Google OAuth 2.0  

---

## Prerequisites

- Python 3.8 or higher  
- Gmail account  
- Google Cloud Console project with Gmail API enabled  

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/swetas7/automatic-email-organizer-1.git
cd automatic-email-organizer-1
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Gmail API

* Go to Google Cloud Console
* Create a new project
* Enable Gmail API
* Create OAuth 2.0 credentials
* Download `credentials.json`
* Place it inside the `auth/` folder

### 4. Run the application

```bash
streamlit run app.py
```

---

## Project Structure

```text
automatic-email-organizer-1/
├── app.py
├── requirements.txt
├── auth/
│   └── credentials.json
├── scripts/
│   ├── fetch_email.py
│   ├── classify_email.py
│   ├── summarize_email.py
│   ├── security_scan.py
│   ├── newsletter.py
│   ├── reply_generator.py
│   └── db.py
└── emails.db
```

---

## Email Categories

* Classes & Lectures
* Exams & Academics
* Assignments & Deadlines
* Placements & Internships
* Club Activities
* Events & Workshops
* Competitions & Hackathons
* Administrative Notices
* Finance & Fees
* General Announcements
* Spam / Promotions

---

## Security and Privacy

* OAuth 2.0 authentication with no password storage
* Emails remain on the user’s local machine
* AI models run locally
* Built-in phishing and suspicious email detection

---

## Team

- Sweta – Backend development and Gmail API integration  
- Manasvi – AI model integration and Streamlit user interface  
- Geet – Email processing pipeline, batch processing, and security scanning  
- Sresth – Smart unsubscribe functionality and AI-based reply generation  


## Hackathon Submission

This project was developed for Hackathon 2026, focusing on productivity, automation, and email security using artificial intelligence.

```
