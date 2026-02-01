import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from scripts.fetch_email import gmail_authenticate, fetch_unread_emails
from scripts.classify_email import classify_email, apply_label_to_email
from scripts.summarize_email import summarize_email
from scripts.reply_generator import generate_reply
from scripts.db import init_db, save_email, get_all_emails
from scripts.security_scan import scan_email
from scripts.newsletter import is_newsletter

# Page Config
st.set_page_config(
    page_title="AI Email Organizer",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
init_db()

# Calculate date filters
def get_date_filter(time_option):
    today = datetime.now()
    if time_option == "Today":
        return today.strftime("%Y/%m/%d")
    elif time_option == "1 day ago":
        return (today - timedelta(days=1)).strftime("%Y/%m/%d")
    elif time_option == "2 days ago":
        return (today - timedelta(days=2)).strftime("%Y/%m/%d")
    elif time_option == "7 days ago":
        return (today - timedelta(days=7)).strftime("%Y/%m/%d")
    else:
        return None  # All emails

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    

    
    # Time Range - in days
    st.subheader("📅 Time Range")
    time_range = st.selectbox(
        "Fetch emails from:",
        ["Today", "1 day ago", "2 days ago", "7 days ago", "All"],
        index=0
    )
    
    st.markdown("---")
    
    # Filter by Category
    st.subheader("📁 Filter by Category")
    st.caption("Click to filter emails:")
    
    # Get all emails for counts
    all_emails_for_count = get_all_emails()
    df_count = pd.DataFrame(all_emails_for_count) if all_emails_for_count else pd.DataFrame()
    
    # Category list
    categories = [
        "All Emails",
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
    
    # Store selected category in session state
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All Emails"
    
    for cat_name in categories:
        # Get count for this category
        if not df_count.empty and cat_name != "All Emails":
            count = len(df_count[df_count['category'] == cat_name])
        else:
            count = len(df_count) if cat_name == "All Emails" else 0
        
        button_label = f"{cat_name} ({count})"
        if st.button(button_label, key=f"cat_{cat_name}", use_container_width=True):
            st.session_state.selected_category = cat_name
    
    st.markdown("---")
    st.caption("Made for Hackathon 🚀")

# Main Content
st.title("📧 Automatic Email Organizer")
st.caption("Powered by AI • Automatically classify and label your emails")

# Get existing emails for stats
all_emails = get_all_emails()
df = pd.DataFrame(all_emails) if all_emails else pd.DataFrame()

# Stat Cards Row
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Emails Processed", value=len(df))

with col2:
    unique_categories = df['category'].nunique() if not df.empty else 0
    st.metric(label="Categories Used", value=unique_categories)

with col3:
    top_category = df['category'].mode()[0] if not df.empty else "None"
    display_cat = top_category[:18] + "..." if len(str(top_category)) > 18 else top_category
    st.metric(label="Top Category", value=display_cat)

st.markdown("---")

# Process Section and Recent Emails
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🚀 Process Emails")
    
    process_btn_label = f"⚡ Process All ({time_range})"
    
    if st.button(process_btn_label, type="primary", use_container_width=True):
        with st.spinner("Processing emails..."):
            try:
                emails = []
                service = None
                
                # Get date filter based on selection
                date_filter = get_date_filter(time_range)

                st.info("Connecting to Gmail...")
                service = gmail_authenticate()
                emails = fetch_unread_emails(service, max_results=50, date_filter=date_filter, only_unread=False)
                
                if emails:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    count = 0
             # Filter out emails already in database
                    existing_ids = [e['id'] for e in get_all_emails()]
                    emails = [e for e in emails if e['id'] not in existing_ids]
                    for i, email in enumerate(emails):
                        status_text.text(f"Processing: {email['subject'][:35]}...")
                        
                        # Skip emails with empty body (can't classify empty text)
                        if not email["body"] or len(email["body"].strip()) < 10:
                            status_text.text(f"Skipping: {email['subject'][:35]}... (empty body)")
                            continue
                        
                        # AI Classification
                        label, score = classify_email(email["body"])
                        
                        # AI Summarization
                        summary = summarize_email(email["body"])
                        
                        # AI Reply Draft
                        reply = generate_reply(label, email["from"], email["body"])
                        
                        # Security Scan
                        is_safe, reason = scan_email(email["subject"], email["body"], email["from"])
                        
                        # Newsletter Check
                        newsletter_flag = is_newsletter(email["from"], email["subject"], email["body"])
                        
                        # Apply Gmail Label
                        apply_label_to_email(service, email["id"], label)
                        
                        # Save to DB
                        is_phishing_int = 0 if is_safe else 1
                        is_newsletter_int = 1 if newsletter_flag else 0
                        
                        if save_email(email, label, summary, reply, is_phishing_int, reason, is_newsletter_int):
                            count += 1
                        
                        progress_bar.progress((i + 1) / len(emails))
                        
                    status_text.empty()
                    st.success(f"Processed {len(emails)} emails! ({count} new saved)")
                    st.rerun()
                else:
                    st.info("No unread emails found for the selected time range.")
            
            except Exception as e:
                st.error(f"Error: {e}")

with col_right:
    selected_cat = st.session_state.selected_category
    st.subheader(f"📬 Recent Emails ({selected_cat})")
    
    if not df.empty:
        date_filter = get_date_filter(time_range)
        if date_filter and time_range != "All":
            try:
                                # Clean timestamp - remove (IST) suffix
                df['timestamp_clean'] = df['timestamp'].astype(str).str.replace(r'\s*\([^)]*\)\s*$', '', regex=True)
                # Convert to datetime
                df['parsed_date'] = pd.to_datetime(df['timestamp_clean'], format='mixed', dayfirst=True, errors='coerce')
                # Compare with filter date
                filter_datetime = pd.to_datetime(date_filter, format='%Y/%m/%d')
                filtered_df = df[df['parsed_date'] >= filter_datetime]
            except:
                filtered_df = df
        else:
            filtered_df = df
        
        # Then filter by category
        if selected_cat != "All Emails":
            filtered_df = filtered_df[filtered_df['category'] == selected_cat]
        
        if not filtered_df.empty:
            for index, row in filtered_df.iterrows():
                with st.expander(f"**{row['subject']}** • {row['category']}", expanded=False):
                    st.markdown(f"**From:** {row['from']}")
                    st.markdown(f"**Time:** {row['timestamp']}")
                    
                    # Security Alert
                    if row['is_phishing'] == 1:
                        st.error(f"⚠️ SECURITY ALERT: {row['security_reason']}")
                    else:
                        st.success("✅ Safe")
                    
                    if row['is_newsletter'] == 1:
                        st.info("📰 Newsletter detected")
                    
                    st.markdown("---")
                    st.info(f"**AI Summary:** {row['summary']}")
                    
                    if row['suggested_reply']:
                        with st.expander("💬 Suggested Reply"):
                            st.text(row['suggested_reply'])
                    
                    with st.expander("📄 Full Email Body"):
                        body_text = str(row['body']) if row['body'] else ""
                        st.text(body_text[:500] + "..." if len(body_text) > 500 else body_text)
        else:
            st.info(f"No emails in '{selected_cat}' category.")
    else:
        st.info("No emails found. Click 'Process All' to fetch and classify emails!")

# Insights Section
st.markdown("---")
st.subheader("📊 Insights")

if not df.empty:
    col_chart, col_stats = st.columns([2, 1])
    
    with col_chart:
        # Category Distribution Chart
        chart_data = df["category"].value_counts().reset_index()
        chart_data.columns = ["Category", "Count"]
        
        c = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Count", stack=True),
            color=alt.Color("Category", scale={"scheme": "tableau10"}),
            tooltip=["Category", "Count"]
        ).properties(height=300)
        
        st.altair_chart(c, use_container_width=True)
    
    with col_stats:
        st.markdown("**Quick Stats:**")
        st.write(f"📧 Total Emails: {len(df)}")
        st.write(f"🏷️ Categories: {df['category'].nunique()}")
        
        phishing_count = df['is_phishing'].sum() if 'is_phishing' in df.columns else 0
        newsletter_count = df['is_newsletter'].sum() if 'is_newsletter' in df.columns else 0
        
        st.write(f"⚠️ Security Alerts: {phishing_count}")
        st.write(f"📰 Newsletters: {newsletter_count}")
else:
    st.info("Sync emails to see insights.")

# Footer
st.markdown("---")
st.caption("🤖 Powered by AI • Built for Hackathon 2026")
