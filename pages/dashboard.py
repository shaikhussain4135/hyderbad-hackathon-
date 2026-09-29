"""Dashboard overview page."""
import streamlit as st
import pandas as pd
from services.resolution_service import ResolutionService
from data.seed_data import seed_database_and_memory
from database.database import get_connection_info
from memory.hindsight_manager import memory_manager
from utils.config import config


def render_dashboard_page():
    st.title("📊 Support Agent Operations Dashboard")
    st.markdown(
        "Monitor live metrics, customer tickets, and **Hindsight Memory** effectiveness across all support interactions."
    )

    # Top Status Bar
    db_name, is_neon = get_connection_info()
    hs_ok, _ = memory_manager.test_connection()

    col_stat1, col_stat2, col_stat3 = st.columns([1, 1, 1])
    with col_stat1:
        st.caption(f"Database: **{db_name}** {'🟢' if is_neon else '🔵 (Configurable to Neon)'}")
    with col_stat2:
        st.caption(f"Hindsight Engine: **{'Connected (Server)' if hs_ok else 'Active (Local Persistent Bank)'}** {'🟢' if hs_ok else '🟠'}")
    with col_stat3:
        st.caption(f"LLM Provider: **{config.llm_provider.upper()}** ({config.llm_model})")

    st.divider()

    # Seed data action & metrics
    metrics = ResolutionService.get_dashboard_metrics()

    # KPI Metric Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Customers", metrics["total_customers"])
    kpi2.metric("Total Tickets", metrics["total_tickets"])
    kpi3.metric("Resolved Tickets", f"{metrics['resolved_tickets']} ({metrics['resolution_rate']}%)")
    kpi4.metric("🧠 Memory-Assisted", metrics["memory_assisted_resolutions"])
    kpi5.metric("Avg Resolution Time", f"{metrics['average_resolution_time_mins']} min")

    st.divider()

    # Quick demo seeder action
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(
            "💡 **Demo Data Readiness:** Initialize realistic demonstration customers "
            "(John Smith with PDF history, Sarah Connor with session timeout history, and Alex Rivera for fresh interactions)."
        )
    with col_btn:
        if st.button("⚡ Seed Demo Data", type="primary", use_container_width=True):
            seed_database_and_memory()
            st.success("Demo dataset seeded!")
            st.rerun()

    st.divider()

    # Value Proposition Visual Banner
    st.subheader("🚀 Memory Value Comparison")
    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        st.error("❌ WITHOUT MEMORY (Generic Support)")
        st.markdown(
            "- Repeats generic diagnostic steps for every ticket\n"
            "- Fails to recognize identical repeat symptoms\n"
            "- Ignores unique customer environment and past fixes\n"
            "- Results in slower resolution times and customer frustration"
        )
    with cmp_col2:
        st.success("🧠 WITH HINDSIGHT MEMORY (Personalized & Fast)")
        st.markdown(
            "- Recalls previous verified root cause immediately\n"
            "- Adapts advice directly to customer environment & plan\n"
            "- Bypasses redundant isolation steps\n"
            "- Continuously learns from every customer feedback outcome"
        )

    st.divider()

    # Recent Activity Tables
    tab1, tab2 = st.tabs(["📋 Recent Tickets", "✅ Recent Resolutions & Memory Outcomes"])

    with tab1:
        if metrics["recent_tickets"]:
            df_tickets = pd.DataFrame(metrics["recent_tickets"])
            display_cols = ["ticket_id", "customer_name", "issue", "category", "severity", "status", "created_at"]
            st.dataframe(df_tickets[[c for c in display_cols if c in df_tickets.columns]], use_container_width=True)
        else:
            st.info("No tickets created yet. Click 'Seed Demo Data' above or create a new ticket.")

    with tab2:
        if metrics["recent_resolutions"]:
            df_res = pd.DataFrame(metrics["recent_resolutions"])
            display_cols = ["resolution_id", "ticket_id", "root_cause", "solution", "outcome", "resolution_time", "customer_feedback"]
            st.dataframe(df_res[[c for c in display_cols if c in df_res.columns]], use_container_width=True)
        else:
            st.info("No resolutions recorded yet.")
