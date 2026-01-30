import streamlit as st
import pandas as pd
import altair as alt
from scripts.fetch_email import gmail_authenticate, fetch_unread_emails, fetch_demo_emails
from scripts.classify_email import classify_email, apply_label_to_email
from scripts.summarize_email import summarize_email
from scripts.reply_generator import generate_reply
from scripts.db import init_db, save_email, get_all_emails
from scripts.security_scan import scan_email
from scripts.newsletter import is_newsletter

# Page Config
# Page Config
st.set_page_config(
    page_title="AI Email Organizer",
    page_icon="None",
    layout="wide"
)

# Initialize DB
init_db()

# Title and Header
st.title("Automatic Email Organizer")
st.write("Using AI to classify and organize your inbox.")

# Sidebar for actions
with st.sidebar:
    st.header("Actions")
    
    use_demo = st.toggle("Demo Mode", value=True, help="Use fake emails if you don't have credentials.")

    if st.button("Sync Last 10 Emails"):
        with st.spinner("Processing..."):
            try:
                emails = []
                service = None

                if use_demo:
                    st.warning("Running in DEMO MODE (Fake Data)")
                    emails = fetch_demo_emails()
                else:
                    st.toast("Connecting to Gmail...", icon="None")
                    service = gmail_authenticate()
                    emails = fetch_unread_emails(service, max_results=10)
                
                if emails:
                    st.toast(f"Fetched {len(emails)} emails! Organizing...", icon="None")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    count = 0
                    for i, email in enumerate(emails):
                        status_text.text(f"Processing: {email['subject'][:40]}...")
                        
                        # AI Classification
                        label, score = classify_email(email["body"])
                        
                        # AI Summarization
                        summary = summarize_email(email["body"])
                        
                        # AI Reply Draft
                        reply = generate_reply(label, email["from"], email["body"])
                        
                        # Phase 4: Security Scan
                        is_safe, reason = scan_email(email["subject"], email["body"], email["from"])
                        
                        # Phase 5: Newsletter Check
                        newsletter_flag = is_newsletter(email["from"], email["subject"], email["body"])
                        
                        # Label Gmail (Only in Real Mode)
                        if not use_demo:
                            apply_label_to_email(service, email["id"], label)
                        
                        # Save to DB
                        # Convert bool to int for SQLite (True=1, False=0)
                        is_phishing_int = 0 if is_safe else 1
                        is_newsletter_int = 1 if newsletter_flag else 0
                        
                        if save_email(email, label, summary, reply, is_phishing_int, reason, is_newsletter_int):
                            count += 1
                        
                        progress_bar.progress((i + 1) / len(emails))
                        
                    status_text.empty()
                    st.success(f"Processed {len(emails)} emails! ({count} new saved)")
                    st.rerun()
                else:
                    st.info("No unread emails found.")
            
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.write("Made for Hackathon")

# Main Content Area
col1, col2 = st.columns([2, 1])

# Fetch data for display
emails = get_all_emails()
df = pd.DataFrame(emails)

with col1:
    st.subheader("Recent Emails")
    if not df.empty:
        # Display as a Clean List with Summaries & Replies
        for index, row in df.iterrows():
            with st.expander(f"**{row['subject']}** ({row['category']})"):
                st.markdown(f"**Sender:** {row['from']}")
                st.markdown(f"**Time:** {row['timestamp']}")
                
                # Security Alert
                if row['is_phishing'] == 1:
                     st.error(f"[SECURITY ALERT] {row['security_reason']}")
                
                st.info(f"**AI Summary:** {row['summary']}")
                
                if row['is_newsletter'] == 1:
                    if st.button("Unsubscribe", key=f"unsub_{row['id']}"):
                        st.success("Successfully Unsubscribed (Simulated)")
                
                if row['suggested_reply']:
                    st.text_area("Suggested Reply:", value=row['suggested_reply'], height=150, key=row['id'])
                
                st.text(row['body'][:500] + "...")
                
    else:
        st.info("No emails organized yet. Click 'Sync Last 10 Emails'!")

with col2:
    st.subheader("📊 Insights")
    if not df.empty:
        # Category Distribution Chart
        chart_data = df["category"].value_counts().reset_index()
        chart_data.columns = ["Category", "Count"]
        
        c = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Count", stack=True),
            color=alt.Color("Category", scale={"scheme": "tableau10"}),
            tooltip=["Category", "Count"]
        ).properties(height=300)
        
        st.altair_chart(c, use_container_width=True)
    else:
        st.write("Sync emails to see insights.")
