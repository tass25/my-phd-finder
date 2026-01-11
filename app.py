import streamlit as st
import sqlite3
import pandas as pd
import os
from config import DB_PATH, CV_PATH, logger
from src.agents import MessageBus
from src.orchestrator import OrchestratorAgent
from src.research import ResearchAgent
from src.verification import VerificationAgent
from src.outreach import OutreachAgent
from src.tools import WebSearch, WebScraper, RankingCalculator, CVParser

# Page Config
st.set_page_config(
    page_title="PhD Finder AI | Autonomous Research System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme
st.markdown("""
    <style>
    /* Dark Theme */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stApp {
        background-color: #0e1117;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d24;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    /* Metrics */
    .stMetric {
        background-color: #1a1d24;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .stMetric label {
        color: #a0a0a0 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    /* Tables */
    .stDataFrame {
        background-color: #1a1d24;
    }
    /* Text */
    h1, h2, h3, p, label, span {
        color: #ffffff !important;
    }
    /* Progress bars */
    .stProgress > div > div {
        background-color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

from src.learning import LearningAgent

# Initialize agents
@st.cache_resource
def get_agents():
    bus = MessageBus()
    search = WebSearch()
    scraper = WebScraper()
    ranker = RankingCalculator()
    cv_parser = CVParser()
    
    research = ResearchAgent(search, scraper, ranker)
    verification = VerificationAgent()
    outreach = OutreachAgent()
    learning = LearningAgent()
    orchestrator = OrchestratorAgent(bus)
    
    bus.register_agent(research)
    bus.register_agent(verification)
    bus.register_agent(outreach)
    bus.register_agent(learning)
    bus.register_agent(orchestrator)
    
    return orchestrator, bus, cv_parser

orchestrator, bus, cv_parser = get_agents()

# Sidebar: Parameters & CV
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Settings")
    
    country = st.text_input("🎯 Target Country", value="Germany", help="Where do you want to find your PhD?")
    
    st.divider()
    st.subheader("📄 Your Profile")
    uploaded_cv = st.file_uploader("Upload CV (PDF)", type="pdf")
    
    if uploaded_cv:
        with open(CV_PATH, "wb") as f:
            f.write(uploaded_cv.getbuffer())
        st.success("CV Uploaded Successfully!")
        
    cv_btn = st.button("🔍 Parse Profile")
    if cv_btn:
        if os.path.exists(CV_PATH):
            profile_text = cv_parser.parse_cv(CV_PATH)
            st.session_state.profile = profile_text
            st.write("Profile extracted and cached.")
        else:
            st.error("Please upload a CV first.")

    st.divider()
    if st.button("🚀 RUN AUTONOMOUS FLOW", type="primary"):
        if 'profile' not in st.session_state:
            st.warning("Please parse your CV profile first.")
        else:
            # Create progress tracking
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Phase 1
                status_text.markdown("### 🔍 Phase 1/5: Discovering Universities")
                progress_bar.progress(20)
                
                # Run the flow
                result = orchestrator.process({
                    "action": "run_full_flow", 
                    "country": country, 
                    "student_profile": st.session_state.get('profile', '')
                })
                
                # Complete
                status_text.markdown("### ✅ All Phases Complete!")
                progress_bar.progress(100)
                
            st.success("🎉 Autonomous search completed! Check the results below.")
            st.balloons()
            
            # Force refresh to show new data
            import time
            time.sleep(1)
            st.rerun()

# Main Page Layout
st.title("🎓 PhD Finder Dashboard")
st.caption("Empowering your academic journey with Autonomous AI Agents")

# Live Activity Monitor
with st.expander("📊 Live Activity Monitor", expanded=True):
    log_container = st.container()
    with log_container:
        try:
            with open("agent_system.log", "r") as f:
                logs = f.readlines()
                recent_logs = logs[-20:]  # Show last 20 lines
                log_text = "".join(recent_logs)
                st.code(log_text, language="log")
        except FileNotFoundError:
            st.info("No activity logs yet. Start the autonomous flow to see live updates!")

# Metrics row
m1, m2, m3, m4 = st.columns(4)
conn = sqlite3.connect(DB_PATH)
u_count = cursor = conn.execute("SELECT count(*) FROM universities").fetchone()[0]
p_count = cursor = conn.execute("SELECT count(*) FROM professors").fetchone()[0]
e_count = cursor = conn.execute("SELECT count(*) FROM emails").fetchone()[0]
v_count = cursor = conn.execute("SELECT count(*) FROM universities WHERE verification_status='verified'").fetchone()[0]
conn.close()

m1.metric("Universities Discovered", u_count)
m2.metric("Professors Matched", p_count)
m3.metric("Emails Drafted", e_count)
m4.metric("Data Verified", f"{v_count}/{u_count}" if u_count > 0 else "0/0")

# Results Tabs
tab1, tab2, tab3 = st.tabs(["🏛 Universities", "👨‍🔬 Professors", "📧 Email Drafts"])

with tab1:
    st.subheader("Top University Matches")
    conn = sqlite3.connect(DB_PATH)
    unis_df = pd.read_sql_query("""
        SELECT name, ranking_qs as 'Rank', match_score as 'Match %', 
               verification_status as 'Status', match_reasoning as 'Reasoning'
        FROM universities 
        ORDER BY match_score DESC
    """, conn)
    st.dataframe(unis_df, use_container_width=True, hide_index=True)
    conn.close()

with tab2:
    st.subheader("Identified Professors")
    conn = sqlite3.connect(DB_PATH)
    profs_df = pd.read_sql_query("""
        SELECT p.name, u.name as 'University', p.department, p.contact_priority as 'Priority', p.accepting_students as 'Recruiting'
        FROM professors p
        JOIN universities u ON p.university_id = u.id
        ORDER BY p.contact_priority DESC
    """, conn)
    st.dataframe(profs_df, use_container_width=True, hide_index=True)
    conn.close()

with tab3:
    st.subheader("Generated Outreach Emails")
    conn = sqlite3.connect(DB_PATH)
    emails = pd.read_sql_query("""
        SELECT p.name as 'Professor', e.subject, e.body, e.quality_score as 'Quality'
        FROM emails e
        JOIN professors p ON e.professor_id = p.id
    """, conn)
    for idx, row in emails.iterrows():
        with st.expander(f"✉️ Email for {row['Professor']} - Score: {row['Quality']}/100"):
            st.text(f"Subject: {row['subject']}")
            st.divider()
            st.text_area("Body", value=row['body'], height=200, key=f"email_{idx}")
            st.button("✅ Approve & Send", key=f"send_{idx}")
    conn.close()

# Agent Logs at the bottom
st.divider()
with st.expander("🛠 Agent Activity Logs (Reasoning Trace)"):
    conn = sqlite3.connect(DB_PATH)
    logs_df = pd.read_sql_query("""
        SELECT agent_name as 'Agent', task, decision, reasoning 
        FROM agent_decisions 
        ORDER BY created_at DESC 
        LIMIT 20
    """, conn)
    st.table(logs_df)
    conn.close()
