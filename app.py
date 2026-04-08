import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Multi-Agent Workspace", layout="wide", initial_sidebar_state="expanded")

import time
from database.db_setup import SessionLocal, Task, CalendarEvent, InternalCRM
from agents.graph import build_graph
from langchain_core.messages import HumanMessage
from database.db_setup import init_db

# Initialize database logic on load
try:
    init_db()
except Exception as e:
    st.error(f"Database Initialization Error: {e}")

# Custom UI
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    code {
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2>🤖 Enterprise Multi-Agent Workspace</h2>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout split
chat_col, ws_col = st.columns([1, 1.2])

with chat_col:
    st.subheader("Mission Control")
    
    # Show history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input
    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.status("Agent Orchestrator is thinking...", expanded=True) as status:
                graph = build_graph()
                # Initialize state with completed_workers
                state = {"messages": [HumanMessage(content=prompt)], "active_context": [], "completed_workers": []}
                
                # Stream the state updates to the UI live
                try:
                    for output in graph.stream(state, config={"recursion_limit": 15}):
                        for node_name, state_upsert in output.items():
                            st.write(f"⚡ **{node_name}**")
                            if "active_context" in state_upsert and state_upsert["active_context"]:
                                for ctx_log in state_upsert["active_context"]:
                                    st.code(ctx_log)
                            
                            # Snag the dynamic summary from the Final_Reporter
                            if node_name == "Final_Reporter" and "messages" in state_upsert:
                                final_msg = state_upsert["messages"][0].content
                                st.session_state.messages.append({"role": "assistant", "content": final_msg})
                    
                    status.update(label="All Workflows Completed ✨", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"**API Quota Error**: The selected model triggered a rate limit (429 Resource Exhausted) from Google Cloud. Please wait exactly 60 seconds for your quota bucket to refill.\n\nRaw diagnostic: {e}")
                    status.update(label="Workflow Failed due to Quota Limit ❌", state="error", expanded=True)
            
            st.rerun()

with ws_col:
    st.subheader("Live Operations Hub")
    tab_crm, tab_jira, tab_cal = st.tabs(["📇 CRM Status", "🎫 Jira Tracker", "📅 Calendar"])
    
    session = SessionLocal()
    
    with tab_crm:
        crm_records = session.query(InternalCRM).all()
        if not crm_records:
            st.info("CRM is currently empty. Trigger an agent event to populate.")
        else:
            # Table Header for better alignment
            h1, h2, h3 = st.columns([1.2, 1.2, 1.2])
            h1.markdown("**Company**")
            h2.markdown("**SLA Tier**")
            h3.markdown("**Current Status**")
            st.divider()

            for rec in crm_records:
                status_map = {
                    "Active": "green",
                    "Warning": "orange",
                    "Maintenance": "#38BDF8", # Sky blue
                    "Critical Outage Reported": "red"
                }
                color = status_map.get(rec.status, "red")
                
                col1, col2, col3 = st.columns([1.2, 1.2, 1.2])
                col1.markdown(f"**{rec.company_name}**")
                col2.markdown(f"`{rec.sla_level}`")
                col3.markdown(f"<b style='color:{color}'>{rec.status}</b>", unsafe_allow_html=True)
                
    with tab_jira:
        tasks = session.query(Task).order_by(Task.id.desc()).limit(10).all()
        if not tasks:
            st.info("No tasks created yet.")
        else:
            for t in tasks:
                st.warning(f"**[{t.status}]** {t.description} (Created: {t.created_at.strftime('%H:%M:%S')})")
                
    with tab_cal:
        events = session.query(CalendarEvent).order_by(CalendarEvent.id.desc()).limit(5).all()
        if not events:
            st.info("No upcoming meetings booked.")
        else:
            for e in events:
                duration = int((e.end_time - e.start_time).total_seconds() / 60)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success(f"**{e.event_name}** | ⏱️ {duration} mins | 📅 {e.start_time.strftime('%b %d, %Y')} 🕒 {e.start_time.strftime('%I:%M %p')}")
                with col2:
                    # Generate standard .ics meeting invite text fixed to IST
                    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Hackathon AI Agent//EN
BEGIN:VEVENT
UID:{e.id}@multi-agent.local
DTSTAMP:{e.start_time.strftime('%Y%m%dT%H%M%S')}
DTSTART;TZID=Asia/Kolkata:{e.start_time.strftime('%Y%m%dT%H%M%S')}
DTEND;TZID=Asia/Kolkata:{e.end_time.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{e.event_name}
DESCRIPTION:Scheduled automatically by the Enterprise AI Assistant.
END:VEVENT
END:VCALENDAR"""
                    st.download_button("📥 Add to Calendar", data=ics_content, file_name=f"invite_{e.id}.ics", mime="text/calendar", key=f"ics_{e.id}")
                
    session.close()
