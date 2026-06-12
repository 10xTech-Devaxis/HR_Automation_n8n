import pandas as pd
import streamlit as st

# CSV Upload Section
st.subheader("📂 Bulk Upload via CSV")

uploaded_file = st.file_uploader("CSV file choose karo", type=["csv"])

if uploaded_file is not None:
    df_upload = pd.read_csv(uploaded_file)
    st.write("Preview:", df_upload.head())
    
    # Expected columns check
    required_cols = ['Email', 'Skills', 'Education', 'Status']
    missing = [c for c in required_cols if c not in df_upload.columns]
    
    if missing:
        st.error(f"Yeh columns missing hain: {missing}")
    else:
        if st.button("✅ Sheet mein upload karo"):
            # Google Sheet mein add karo
            ws = sh.sheet1
            for _, row in df_upload.iterrows():
                ws.append_row([
                    row.get('Email', ''),
                    row.get('Task_Link', 'task.com'),
                    row.get('Education', ''),
                    row.get('Skills', ''),
                    row.get('Status', 'new'),
                    'pending'  # Email_sent
                ])
            st.success(f"{len(df_upload)} candidates upload ho gaye!")
            st.cache_data.clear()
            st.rerun()
