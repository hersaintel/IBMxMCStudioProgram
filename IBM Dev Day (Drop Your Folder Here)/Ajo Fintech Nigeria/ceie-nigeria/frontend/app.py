import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="CEIE Nigeria", layout="wide", page_icon="🇳🇬")
st.title("CEIE Nigeria: Cooperative Economic Intelligence Platform")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Overview", 
    "👥 Member Identity (MDM)", 
    "⚠️ Fraud Alerts", 
    "📈 Macro Intelligence"
])

def mask_phone(phone):
    if not isinstance(phone, str) or len(phone) < 8: return phone
    return phone[:4] + "*" * (len(phone)-7) + phone[-3:]

def mask_bvn(bvn):
    if not isinstance(bvn, str) or len(bvn) < 5: return bvn
    return bvn[:3] + "*" * (len(bvn)-5) + bvn[-2:]

# Tab 1: Overview
with tab1:
    st.header("Platform Overview")
    
    with st.spinner("Loading statistics..."):
        try:
            stats_res = requests.get(f"{API_BASE}/stats").json()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Transactions", f"{stats_res.get('txn_count', 0):,}")
            c2.metric("Raw Member Records", f"{stats_res.get('raw_count', 0):,}")
            c3.metric("Golden Records", f"{stats_res.get('golden_count', 0):,}", 
                      delta=f"-{stats_res.get('merged', 0)} merged", delta_color="normal")
                      
            st.subheader("NDPA Compliant Member Directory")
            try:
                df = pd.read_csv("data/members_dirty.csv")
                # Apply PII masking
                df['phone'] = df['phone'].apply(mask_phone)
                df['bvn'] = df['bvn'].apply(mask_bvn)
                df['nin'] = df['nin'].apply(mask_bvn) # mask NIN similarly
                st.dataframe(df.head(100), use_container_width=True)
            except Exception:
                st.info("No member data found. Please run Data Ingestion first.")
        except Exception as e:
            st.error("Backend API is unreachable. Please ensure the backend is running.")

# Tab 2: Member Identity (MDM)
with tab2:
    st.header("Master Data Management (Entity Resolution)")
    
    if st.button("Run Matching & Ingestion"):
        with st.spinner("Running Entity Resolution (Local/IBM Match 360)..."):
            try:
                res = requests.post(f"{API_BASE}/ingest").json()
                st.success(f"Ingestion successful! Mode: {res.get('mdm_mode')}")
                st.rerun()
            except Exception as e:
                st.error(f"Ingestion failed: {e}")
                
    with st.spinner("Loading Golden Records..."):
        try:
            golden_res = requests.get(f"{API_BASE}/golden-records").json()
            if golden_res:
                st.write(f"Generated **{len(golden_res)}** golden records.")
                
                # Plot confidence histogram
                confidences = [g.get('match_confidence', 1.0) for g in golden_res]
                fig = px.histogram(x=confidences, nbins=20, labels={'x':'Match Confidence'}, title="Golden Record Confidence Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Prepare table
                table_data = []
                for g in golden_res:
                    record = g['golden_record']
                    table_data.append({
                        "Member ID": record.get('member_id'),
                        "Name": record.get('name'),
                        "Confidence": round(g.get('match_confidence', 0), 2),
                        "Source Count": len(g.get('source_records', [])),
                        "Needs Review": "Yes" if g.get('needs_review') else "No"
                    })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)
            else:
                st.info("No golden records available. Run Matching first.")
        except Exception:
            st.warning("Could not fetch golden records.")

# Tab 3: Fraud Alerts
with tab3:
    st.header("Fraud Intelligence & Alerts")
    
    with st.spinner("Scoring transactions..."):
        try:
            alerts = requests.get(f"{API_BASE}/fraud/alerts").json()
            if alerts:
                st.write(f"Generated **{len(alerts)}** alerts.")
                
                for alert in alerts:
                    sev = alert['severity']
                    icon = "🔴" if sev == "high" else ("🟠" if sev == "medium" else "🟡")
                    
                    with st.expander(f"{icon} [{alert['rule_id']}] {alert['title']} - {alert['member']}"):
                        st.write(f"**Reason:** {alert['reason']}")
                        st.write(f"**Anomaly Score:** {alert['anomaly_score']}")
                        st.caption(f"Audit Trail Timestamp: {alert['timestamp']}")
            else:
                st.success("No fraud alerts detected.")
        except Exception:
            st.error("Failed to load fraud alerts.")

# Tab 4: Macro
with tab4:
    st.header("Macro Intelligence & Chat")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        with st.spinner("Fetching World Bank data..."):
            try:
                macro_res = requests.get(f"{API_BASE}/macro").json()
                if len(macro_res) > 1:
                    data_points = macro_res[1]
                    df_macro = pd.DataFrame(data_points)
                    df_macro = df_macro.dropna(subset=['value'])
                    df_macro['date'] = pd.to_numeric(df_macro['date'])
                    df_macro = df_macro.sort_values('date')
                    
                    fig = px.line(df_macro, x="date", y="value", title="Nigeria Inflation (Annual %)", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.error("Failed to load macro data.")
                
    with c2:
        st.subheader("Ask CEIE Agent")
        question = st.text_input("Ask about fraud, inflation, or duplicates:")
        if question:
            with st.spinner("Thinking..."):
                try:
                    ans = requests.post(f"{API_BASE}/query", json={"question": question}).json()
                    st.info(ans['answer'])
                except Exception:
                    st.error("Agent unavailable.")
