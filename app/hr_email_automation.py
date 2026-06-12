import streamlit as st
import pandas as pd
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# EMAIL TEMPLATES
# -----------------------------
TEMPLATES = {
    "new": {
        "label": "📩 New – Application Received",
        "color": "#63b3ed",
        "subject": "Next steps for your application - {{Name}}",
        "body": """Hi {{Name}},

Thank you for applying. We are impressed with your background in {{Education}}.

To move forward in the process, please complete the technical task using the link below:
{{Task_Link}}

We look forward to your response.

Best regards,
HR Team"""
    },
    "shortlisted": {
        "label": "🎉 Shortlisted – Congratulations",
        "color": "#68d391",
        "subject": "Congratulations {{Name}} - You're Shortlisted!",
        "body": """Hi {{Name}},

Your skills in {{Skills}} align well with our requirements.

We are pleased to inform you that you have been shortlisted for the next round of the selection process.

We will share further updates soon.

Best regards,
HR Team"""
    },
    "completed": {
        "label": "✅ Completed – Process Done",
        "color": "#b794f4",
        "subject": "Application Update - {{Name}}",
        "body": """Hi {{Name}},

Thank you for completing the entire selection process.

We appreciate your time and effort throughout the application journey.

We will reach out to you soon with the final update.

Best regards,
HR Team"""
    }
}

# Status mapping — blank/new → new, shortlisted → shortlisted, completed → completed
# Rejected aur kuch bhi aur → no email
def get_template_key(status_raw):
    s = str(status_raw).strip().lower()
    if s in ("", "new", "blank"):
        return "new"
    elif s in ("shortlisted", "selected"):
        return "shortlisted"
    elif s == "completed":
        return "completed"
    else:
        return None  # rejected ya kuch bhi → email nahi


# -----------------------------
# TEMPLATE ENGINE
# -----------------------------
def fill_template(template, data):
    for key, value in data.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


# -----------------------------
# SENT LOG
# -----------------------------
LOG_FILE = "sent_log.json"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="HR Email Automation", page_icon="📧", layout="wide")

st.title("📧 HR Email Automation System")

# Email logic info box
st.markdown("""
<div style="background:#1a1a2e;border-radius:10px;padding:1rem 1.5rem;margin-bottom:1.5rem;border-left:4px solid #63b3ed;">
    <strong style="color:#63b3ed;">⚡ Auto Email Logic</strong><br><br>
    <span style="color:#63b3ed;">● blank / new</span> → Application Received mail<br>
    <span style="color:#68d391;">● shortlisted / selected</span> → Congratulations mail<br>
    <span style="color:#b794f4;">● completed</span> → Process Complete mail<br>
    <span style="color:#718096;">● rejected / anything else</span> → No email sent
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 CSV Bulk Send", "✏️ Single Candidate", "📧 Email Templates"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CSV BULK SEND
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📋 Bulk Email via CSV")
    st.markdown("CSV mein ye columns hone chahiye: `Name, Email, Education, Skills, Task_Link, Status`")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Candidate CSV", type=["csv"])
    with col2:
        dry_run = st.checkbox("🔍 Dry Run (emails nahi jayenge, sirf preview hoga)", value=True)

    # Gmail credentials (only for real send)
    if not dry_run:
        st.markdown("#### Gmail Settings")
        gc1, gc2 = st.columns(2)
        with gc1:
            gmail_user = st.text_input("Gmail Address", placeholder="you@gmail.com")
        with gc2:
            gmail_pass = st.text_input("Gmail App Password", type="password", placeholder="16-char app password")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        st.markdown("#### 👀 CSV Preview")
        st.dataframe(df, use_container_width=True)

        # Show what will happen per candidate
        st.markdown("#### 📬 Email Plan")
        plan = []
        for _, row in df.iterrows():
            status_raw = row.get("Status", "")
            key = get_template_key(status_raw)
            name = row.get("Name", "")
            email = row.get("Email", "")
            if key:
                t = TEMPLATES[key]
                plan.append({"name": name, "email": email, "status": str(status_raw), "template": key, "label": t["label"], "color": t["color"]})
            else:
                plan.append({"name": name, "email": email, "status": str(status_raw), "template": None, "label": "⛔ No email (rejected/unknown)", "color": "#718096"})

        for p in plan:
            st.markdown(
                f"<div style='padding:8px 14px;margin:4px 0;border-radius:8px;background:#1a1a2e;border-left:3px solid {p['color']};'>"
                f"<strong>{p['name']}</strong> ({p['email']}) — Status: <code>{p['status']}</code> → <span style='color:{p['color']};'>{p['label']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        if st.button("🚀 Check & Send Emails"):
            log = load_log()
            results = []

            for _, row in df.iterrows():
                name      = str(row.get("Name", "")).strip()
                email     = str(row.get("Email", "")).strip()
                education = str(row.get("Education", "")).strip()
                skills    = str(row.get("Skills", "")).strip()
                task_link = str(row.get("Task_Link", "")).strip()
                status_raw= str(row.get("Status", "")).strip()

                key = get_template_key(status_raw)

                if not key:
                    results.append(f"⛔ SKIPPED — {name} ({email}) — status '{status_raw}' → no email")
                    continue

                log_key = f"{email}_{key}"
                if log_key in log:
                    results.append(f"⏭️ ALREADY SENT — {name} ({email}) — '{key}' mail already sent before")
                    continue

                t = TEMPLATES[key]
                data = {"Name": name, "Education": education, "Skills": skills, "Task_Link": task_link}
                subject = fill_template(t["subject"], data)
                body    = fill_template(t["body"], data)

                if dry_run:
                    results.append(f"✅ DRY RUN → would send '{key}' mail to {name} <{email}>")
                else:
                    try:
                        msg = MIMEMultipart()
                        msg["From"]    = gmail_user
                        msg["To"]      = email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(body, "plain"))

                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls()
                        server.login(gmail_user, gmail_pass)
                        server.sendmail(gmail_user, email, msg.as_string())
                        server.quit()

                        log[log_key] = {"name": name, "template": key, "sent": True}
                        save_log(log)
                        results.append(f"📧 SENT — '{key}' mail sent to {name} <{email}>")
                    except Exception as e:
                        results.append(f"❌ ERROR — {name} ({email}) — {str(e)}")

            st.markdown("#### 📊 Result")
            for r in results:
                color = "#68d391" if "SENT" in r or "DRY RUN" in r else "#fc8181" if "ERROR" in r else "#a0aec0"
                st.markdown(f"<div style='padding:6px 12px;margin:3px 0;border-radius:6px;background:#1a1a2e;color:{color};font-family:monospace;'>{r}</div>", unsafe_allow_html=True)

            if not dry_run:
                st.success("✅ Done! Sent log saved.")

        if st.button("🔄 Reset 'already sent' log"):
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
            st.success("Log reset! Ab sab candidates ko dobara send hoga.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SINGLE CANDIDATE
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("✏️ Single Candidate Email")

    c1, c2 = st.columns(2)
    with c1:
        name      = st.text_input("Name *")
        email_to  = st.text_input("Email *")
        education = st.text_input("Education")
    with c2:
        skills    = st.text_input("Skills")
        task_link = st.text_input("Task Link (New ke liye)")
        status_input = st.selectbox("Status *", ["new", "shortlisted", "completed", "rejected", "blank"])

    key = get_template_key(status_input)

    if key:
        t = TEMPLATES[key]
        data = {"Name": name or "{{Name}}", "Education": education or "{{Education}}",
                "Skills": skills or "{{Skills}}", "Task_Link": task_link or "{{Task_Link}}"}
        subject = fill_template(t["subject"], data)
        body    = fill_template(t["body"], data)

        st.markdown(f"""
        <div style="background:#1a1a2e;border-radius:10px;padding:1rem 1.5rem;margin-top:1rem;border-left:4px solid {t['color']};">
            <div style="font-size:0.78rem;color:#718096;margin-bottom:4px;">SUBJECT</div>
            <div style="font-weight:600;color:#e2e8f0;margin-bottom:1rem;">{subject}</div>
            <div style="font-size:0.78rem;color:#718096;margin-bottom:4px;">BODY</div>
            <pre style="white-space:pre-wrap;font-family:sans-serif;color:#cbd5e0;font-size:0.88rem;line-height:1.7;margin:0;">{body}</pre>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⛔ Rejected ya unknown status — koi email nahi jayega!")

    if st.button("🚀 Send Email (Simulated)"):
        if name and email_to and key:
            st.success(f"✅ '{key}' mail sent to {name} <{email_to}> (simulated)")
        elif not key:
            st.warning("⛔ Is status ke liye email nahi bheja jayega!")
        else:
            st.error("⚠️ Name aur Email required hai!")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EMAIL TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📧 Email Templates")

    for key, t in TEMPLATES.items():
        st.markdown(f"""
        <div style="background:#1a1a2e;border-radius:10px;padding:1rem 1.5rem;margin-bottom:1rem;border-left:4px solid {t['color']};">
            <div style="font-weight:700;color:{t['color']};margin-bottom:0.8rem;">{t['label']}</div>
            <div style="font-size:0.78rem;color:#718096;margin-bottom:2px;">SUBJECT</div>
            <div style="color:#e2e8f0;margin-bottom:0.8rem;">{t['subject']}</div>
            <div style="font-size:0.78rem;color:#718096;margin-bottom:2px;">BODY</div>
            <pre style="white-space:pre-wrap;font-family:sans-serif;color:#cbd5e0;font-size:0.85rem;line-height:1.7;margin:0;">{t['body']}</pre>
        </div>
        """, unsafe_allow_html=True)