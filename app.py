"""Customer Support Memory Agent — Main Streamlit Application."""
import streamlit as st
from database.database import init_db, get_connection_info
from memory.hindsight_manager import memory_manager
from utils.config import config
from data.seed_data import seed_database_and_memory
from database.repositories import TicketRepository

# Page configuration
st.set_page_config(
    page_title="Customer Support Memory Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Auto-initialize database schema
try:
    init_db()
    # Check if empty, auto-seed realistic demo data so app is immediately ready
    if len(TicketRepository.list_all()) == 0:
        seed_database_and_memory()
except Exception as e:
    st.error(f"Database initialization warning: {str(e)}")

# Authentication check
if not st.session_state.get("authenticated", False):
    from pages.login import render_login_page
    render_login_page()
    st.stop()

# Sidebar user profile & logout
user = st.session_state.get("user", {})
st.sidebar.markdown(f"### {user.get('avatar', '👤')} {user.get('name', 'Support Agent')}")
st.sidebar.caption(f"Role: **{user.get('role', 'Agent')}**")

if st.sidebar.button("🚪 Sign Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state.pop("user", None)
    st.rerun()

st.sidebar.divider()

# Sidebar navigation & status
st.sidebar.title("🧠 Support Memory AI")
st.sidebar.caption("Persistent Experience Agent via Hindsight")

nav_choice = st.sidebar.radio(
    "Navigation",
    options=[
        "📊 Dashboard",
        "🎫 New Support Ticket",
        "🗂️ Ticket History",
        "🧠 Memory Explorer",
        "📈 Analytics",
        "🔌 Integrations / Settings",
    ],
    index=0,
)

st.sidebar.divider()

# Live Service Status Indicators in Sidebar
st.sidebar.markdown("### 🔌 System Connectivity")
db_name, is_neon = get_connection_info()
hs_live, _ = memory_manager.test_connection()

if is_neon:
    st.sidebar.success(f"🟢 DB: {db_name}")
else:
    st.sidebar.info(f"🔵 DB: {db_name}")

if hs_live:
    st.sidebar.success("🟢 Hindsight: Server Live")
else:
    st.sidebar.warning("🟠 Hindsight: Local Bank Active")

st.sidebar.caption(f"🤖 LLM: **{config.llm_provider.upper()}** ({config.llm_model})")

st.sidebar.divider()
st.sidebar.markdown(
    "**Hackathon Demo Quick Guide:**\n"
    "1. Go to **🎫 New Support Ticket**\n"
    "2. Select **John Smith**\n"
    "3. Click preset *'Main Demo 1 (PDF Upload)'*\n"
    "4. Observe **🧠 Hindsight Memory** recall & personalized response!\n"
    "5. Try **Alex Rivera** (Fresh customer) to verify the *'No Memory'* generic flow."
)

# Route to selected page
if nav_choice == "📊 Dashboard":
    from pages.dashboard import render_dashboard_page
    render_dashboard_page()

elif nav_choice == "🎫 New Support Ticket":
    from pages.new_ticket import render_new_ticket_page
    render_new_ticket_page()

elif nav_choice == "🗂️ Ticket History":
    from pages.ticket_history import render_ticket_history_page
    render_ticket_history_page()

elif nav_choice == "🧠 Memory Explorer":
    from pages.memory_explorer import render_memory_explorer_page
    render_memory_explorer_page()

elif nav_choice == "📈 Analytics":
    from pages.analytics import render_analytics_page
    render_analytics_page()

elif nav_choice == "🔌 Integrations / Settings":
    from pages.integrations import render_integrations_page
    render_integrations_page()
