import streamlit as st
import pandas as pd
import requests
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="HR Automation Dashboard",
    page_icon="👥",
    layout="wide"
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .header-container {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D6A9F 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }

    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-size: 0.95rem;
        opacity: 0.8;
        margin-top: 0.3rem;
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        border-left: 4px solid #2D6A9F;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A5F;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    .card-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1E3A5F;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }

    .guide-step {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid #F3F4F6;
    }

    .step-number {
        background: #1E3A5F;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }

    .step-text {
        font-size: 0.9rem;
        color: #374151;
        line-height: 1.5;
        padding-top: 3px;
    }

    .step-text strong {
        color: #1E3A5F;
    }

    .info-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.85rem;
        color: #1D4ED8;
        margin-top: 1rem;
    }

    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.85rem;
        color: #92400E;
        margin-top: 0.5rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1E3A5F, #2D6A9F) !important;
        color: white !important;
        border: none !important;
        padding: 0.65rem 2.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
    }

    .last-updated {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-align: right;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Google Sheets Connection
# ---------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

WEBHOOK_URL = "http://localhost:5678/webhook/874263e1-de3d-4c5b-8763-8890139c6ee0"

def load_google_sheet():
    try:
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        client = gspread.authorize(creds)
        sheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1L1yPZU7R1q71CQko8JoLpOG4NYQABwm8FdU6A740zvY/edit?gid=1271037269#gid=1271037269"
        )
        worksheet = sheet.get_worksheet_by_id(1271037269)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Google Sheet load failed: {e}")
        return pd.DataFrame()

# ---------------------------
# Load Data
# ---------------------------
df = load_google_sheet()

# ---------------------------
# HEADER
# ---------------------------
now = datetime.now().strftime("%d %b %Y, %I:%M %p")
st.markdown(f"""
<div class="header-container">
    <div class="header-title">👥 HR Automation Dashboard</div>
    <div class="header-subtitle">Candidate pipeline — Last loaded: {now}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# METRICS
# ---------------------------
if not df.empty:
    total = len(df)
    new_count = len(df[df['Status'].str.lower() == 'new']) if 'Status' in df.columns else 0
    shortlisted = len(df[df['Status'].str.lower() == 'shortlisted']) if 'Status' in df.columns else 0
    completed = len(df[df['Status'].str.lower() == 'completed']) if 'Status' in df.columns else 0
    email_sent = len(df[df['Email_sent'] == True]) if 'Email_sent' in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total}</div>
            <div class="metric-label">Total Candidates</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-left-color:#3B82F6">
            <div class="metric-value" style="color:#3B82F6">{new_count}</div>
            <div class="metric-label">New</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-left-color:#10B981">
            <div class="metric-value" style="color:#10B981">{shortlisted}</div>
            <div class="metric-label">Shortlisted</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="border-left-color:#6B7280">
            <div class="metric-value" style="color:#6B7280">{completed}</div>
            <div class="metric-label">Completed</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card" style="border-left-color:#F59E0B">
            <div class="metric-value" style="color:#F59E0B">{email_sent}</div>
            <div class="metric-label">Emails Sent</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------
# MAIN LAYOUT
# ---------------------------
left_col, right_col = st.columns([3, 1])

with left_col:

    # Candidate Table
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Candidate List</div>', unsafe_allow_html=True)

    if not df.empty:
        statuses = ["All"] + sorted(df['Status'].dropna().unique().tolist()) if 'Status' in df.columns else ["All"]
        selected_status = st.selectbox("Filter by Status", statuses, label_visibility="collapsed")
        filtered_df = df if selected_status == "All" else df[df['Status'] == selected_status]
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=300)
        st.markdown(f'<div class="last-updated">Showing {len(filtered_df)} of {len(df)} candidates</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No candidate data found.")

    st.markdown('</div>', unsafe_allow_html=True)

    # How to Use Guide
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📖 HR Guide — Dashboard Kaise Use Karein</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-step">
        <div class="step-number">1</div>
        <div class="step-text">
            <strong>Google Sheet mein candidates add karein</strong><br>
            Apni Google Sheet open karein aur naye candidates ka data fill karein —
            Name, Email, Task_Link, Education, Skills, Status (new/shortlisted/completed).
        </div>
    </div>
    <div class="guide-step">
        <div class="step-number">2</div>
        <div class="step-text">
            <strong>Dashboard refresh karein</strong><br>
            Neeche "↻ Refresh Sheet" button dabayein — latest candidates load ho jayenge.
        </div>
    </div>
    <div class="guide-step">
        <div class="step-number">3</div>
        <div class="step-text">
            <strong>"▶ Run Pipeline" button dabayein</strong><br>
            Ye button saare candidates ko automatically process karega —
            har candidate ko unke status ke hisaab se email chali jayegi.
        </div>
    </div>
    <div class="guide-step">
        <div class="step-number">4</div>
        <div class="step-text">
            <strong>Result dekhe</strong><br>
            Processing ke baad screen pe dikhega kitne candidates successfully process hue.
            Email_sent column Google Sheet mein automatically TRUE ho jayega.
        </div>
    </div>

    <div class="info-box">
        ℹ️ <strong>Aapko kuch manually nahi karna:</strong> Email automatically candidate ke status
        (New / Shortlisted / Completed) ke hisaab se personalized hoti hai aur directly unke inbox mein jaati hai.
    </div>

    <div class="warning-box">
        ⚠️ <strong>Dhyan rakhein:</strong> Pipeline run karne se pehle ensure karein ki Google Sheet mein
        candidate ka Email column sahi bharaa ho — warna email deliver nahi hogi.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right_col:

    # Run Pipeline
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Run Pipeline</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#6B7280; margin-bottom:1rem;'>Saare candidates ko automatically email bhejne ke liye yahan click karein.</p>", unsafe_allow_html=True)

    if st.button("▶ Run Pipeline", disabled=df.empty, key="run_btn"):
        try:
            requests.get("http://localhost:5678", timeout=3)
        except Exception as e:
            st.error(f"❌ n8n not reachable: {e}")
            st.stop()

        errors = []
        success_count = 0
        progress = st.progress(0)
        status_text = st.empty()
        total_rows = len(df)

        for i, (_, row) in enumerate(df.iterrows()):
            candidate = {
                "name": row.get("Name", ""),
                "email": row.get("Email", ""),
                "task_link": row.get("Task_Link", ""),
                "education": row.get("Education", ""),
                "skills": row.get("Skills", ""),
                "status": row.get("Status", ""),
                "email_sent": row.get("Email_sent", "")
            }
            status_text.markdown(f"<small>⏳ Processing <strong>{candidate['name']}</strong>...</small>", unsafe_allow_html=True)

            try:
                response = requests.post(WEBHOOK_URL, json=candidate, timeout=10)
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    errors.append(f"{candidate['name']}: Status {response.status_code}")
            except Exception as e:
                errors.append(f"{candidate['name']}: {str(e)}")

            progress.progress((i + 1) / total_rows)

        status_text.empty()

        if success_count > 0:
            st.success(f"✅ {success_count} candidates processed!")
        if errors:
            st.error("❌ Kuch candidates fail hue:")
            for err in errors:
                st.write(f"• {err}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Refresh
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔄 Refresh Data</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#6B7280; margin-bottom:1rem;'>Google Sheet se latest candidates reload karein.</p>", unsafe_allow_html=True)
    if st.button("↻ Refresh Sheet", key="refresh_btn"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Status Guide
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📌 Status Guide</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.83rem; color:#374151; line-height:2;">
        <span style="background:#DBEAFE;color:#1D4ED8;padding:2px 8px;border-radius:10px;font-weight:600;">new</span> — Naya candidate, pehli baar apply kiya<br>
        <span style="background:#D1FAE5;color:#065F46;padding:2px 8px;border-radius:10px;font-weight:600;">shortlisted</span> — Interview ke liye select hua<br>
        <span style="background:#F3F4F6;color:#374151;padding:2px 8px;border-radius:10px;font-weight:600;">completed</span> — Process complete ho gaya<br>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)