"""Analytics and Improvement Over Time Page."""
import streamlit as st
import pandas as pd
from services.resolution_service import ResolutionService
from database.repositories import TicketRepository, CustomerRepository, ResolutionRepository
from memory.hindsight_manager import memory_manager


def render_analytics_page():
    st.title("📈 Support Intelligence & Performance Analytics")
    st.markdown("Quantify agent efficiency gains, memory utilization, and real empirical resolution improvements.")

    metrics = ResolutionService.get_dashboard_metrics()
    tickets = TicketRepository.list_all()
    resolutions = ResolutionRepository.list_all()
    memories = memory_manager.list_all_memories()

    # Core Metric Highlights
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tickets Handled", metrics["total_tickets"])
    c2.metric("Resolution Rate", f"{metrics['resolution_rate']}%")
    c3.metric("🧠 Memory-Assisted Cases", metrics["memory_assisted_resolutions"])
    c4.metric("Avg Resolution Time", f"{metrics['average_resolution_time_mins']} min")

    st.divider()

    # Empirical Improvement Over Time Analysis
    st.subheader("⏱️ Learning Progression: First vs Later Interactions")
    st.caption("Demonstrating how persistent Hindsight memory reduces repetitive triage across successive customer touchpoints.")

    # Group tickets by customer and sequence
    cust_tickets = {}
    for t in sorted(tickets, key=lambda x: x.created_at):
        cust_tickets.setdefault(t.customer_id, []).append(t)

    first_interaction_times = []
    later_interaction_times = []

    res_map = {r.ticket_id: r for r in resolutions}

    for cust_id, t_list in cust_tickets.items():
        for i, t in enumerate(t_list):
            if t.ticket_id in res_map:
                res_obj = res_map[t.ticket_id]
                if i == 0:
                    first_interaction_times.append(res_obj.resolution_time)
                else:
                    later_interaction_times.append(res_obj.resolution_time)

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("#### 1️⃣ Initial Interactions (Without Prior Memory)")
        avg_first = round(sum(first_interaction_times) / len(first_interaction_times), 1) if first_interaction_times else 0.0
        st.metric("Avg Time to Resolve", f"{avg_first} min", delta=None)
        st.markdown(
            "- **Nature:** Exploratory troubleshooting, manual log inspections\n"
            "- **Memory State:** Baseline diagnostic protocols\n"
            "- **Resolution Type:** Root-cause discovery"
        )

    with col_l2:
        st.markdown("#### 🔄 Repeat / Similar Interactions (With Hindsight Memory)")
        avg_later = round(sum(later_interaction_times) / len(later_interaction_times), 1) if later_interaction_times else 0.0
        time_saved = round(avg_first - avg_later, 1) if (avg_first and avg_later) else 0.0
        st.metric("Avg Time to Resolve", f"{avg_later} min", delta=f"-{time_saved} min (Faster)" if time_saved > 0 else None)
        st.markdown(
            "- **Nature:** Memory-retrieved targeted solution\n"
            "- **Memory State:** Recalled verified past fixes\n"
            "- **Resolution Type:** Instant personalized guidance"
        )

    st.divider()

    # Category and Severity Breakdown
    st.subheader("📊 Ticket Category & Severity Distribution")
    if tickets:
        cat_counts = {}
        sev_counts = {}
        for t in tickets:
            cat_counts[t.category] = cat_counts.get(t.category, 0) + 1
            sev_counts[t.severity] = sev_counts.get(t.severity, 0) + 1

        bcol1, bcol2 = st.columns(2)
        with bcol1:
            st.markdown("**Tickets by Category:**")
            df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"]).set_index("Category")
            st.bar_chart(df_cat)

        with bcol2:
            st.markdown("**Tickets by Severity:**")
            df_sev = pd.DataFrame(list(sev_counts.items()), columns=["Severity", "Count"]).set_index("Severity")
            st.bar_chart(df_sev)
    else:
        st.info("No ticket distribution data yet.")
