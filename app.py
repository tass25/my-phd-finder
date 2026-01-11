import streamlit as st
import sqlite3
import pandas as pd
from config import DB_PATH
from src.agents import MessageBus
from src.orchestrator import OrchestratorAgent
from src.research import ResearchAgent
from src.verification import VerificationAgent
from src.outreach import OutreachAgent
from src.tools import WebSearch, WebScraper, RankingCalculator

# Initialize agents
@st.cache_resource
def get_agents():
    bus = MessageBus()
    
    # Tools
    search = WebSearch()
    scraper = WebScraper()
    ranker = RankingCalculator()
    
    # Agents
    research = ResearchAgent(search, scraper, ranker)
    verification = VerificationAgent()
    outreach = OutreachAgent()
    orchestrator = OrchestratorAgent(bus)
    
    # Register
    bus.register_agent(research)
    bus.register_agent(verification)
    bus.register_agent(outreach)
    bus.register_agent(orchestrator)
    
    return orchestrator, bus

orchestrator, bus = get_agents()

st.set_page_config(page_title="PhD Finder AI", layout="wide")

st.title("🤖 Autonomous PhD Finder AI")

# Sidebar
with st.sidebar:
    st.header("Search Parameters")
    country = st.text_input("Country to Search", value="Germany")
    if st.button("🚀 Start Search"):
        with st.status("Agents are working...", expanded=True) as status:
            st.write("Orchestrator planning...")
            response = orchestrator.process({"action": "start_research", "country": country})
            st.write(response["message"])
            status.update(label="Research Initialized!", state="complete")

# Main Dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎓 Universities Found")
    conn = sqlite3.connect(DB_PATH)
    unis_df = pd.read_sql_query("SELECT name, ranking_qs, match_score, verification_status FROM universities", conn)
    st.dataframe(unis_df, use_container_width=True)
    conn.close()

with col2:
    st.subheader("👨‍🏫 Recommended Professors")
    conn = sqlite3.connect(DB_PATH)
    profs_df = pd.read_sql_query("SELECT name, department, match_score, contact_priority FROM professors", conn)
    st.dataframe(profs_df, use_container_width=True)
    conn.close()

# Recent Activity
st.subheader("📝 Agent Reasoning Log")
conn = sqlite3.connect(DB_PATH)
logs_df = pd.read_sql_query("SELECT agent_name, task, decision, reasoning FROM agent_decisions ORDER BY created_at DESC LIMIT 10", conn)
st.table(logs_df)
conn.close()
