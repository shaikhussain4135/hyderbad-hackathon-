"""Ticket History page."""
import streamlit as st
import pandas as pd
from services.ticket_service import TicketService
from services.customer_service import CustomerService
from services.resolution_service import ResolutionService
from database.repositories import MessageRepository


def render_ticket_history_page():
    st.title("🗂️ Support Ticket History")
    st.markdown("Inspect all historical tickets, complete conversation threads, and resolution audits.")

    # Filter controls
    customers = CustomerService.list_all()
    col_f1, col_f2 = st.columns(2)

    cust_map = {"All Customers": None}
    for c in customers:
        cust_map[f"{c.name} ({c.customer_id})"] = c.customer_id

    with col_f1:
        sel_cust_label = st.selectbox("Filter by Customer", options=list(cust_map.keys()))
        filter_cust = cust_map[sel_cust_label]

    with col_f2:
        sel_status = st.selectbox("Filter by Status", options=["All Statuses", "Open", "Resolved"])
        filter_status = None if sel_status == "All Statuses" else sel_status

    tickets = TicketService.list_tickets(customer_id=filter_cust, status=filter_status)

    if not tickets:
        st.info("No tickets match the selected criteria.")
        return

    # Summary table
    records = []
    for t in tickets:
        res = ResolutionService.get_by_ticket(t.ticket_id)
        records.append({
            "Ticket ID": t.ticket_id,
            "Customer": t.customer.name if t.customer else "Unknown",
            "Issue": t.issue,
            "Category": t.category,
            "Severity": t.severity,
            "Status": t.status,
            "Created Date": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "-",
            "Resolution": res.solution[:60] + "..." if res and res.solution else "-",
            "Time (min)": res.resolution_time if res else "-",
        })

    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True)

    st.divider()

    # Detailed Ticket Inspector
    st.subheader("🔍 Detailed Ticket Inspector")
    ticket_ids = [t.ticket_id for t in tickets]
    chosen_id = st.selectbox("Select Ticket ID to Inspect", options=ticket_ids)

    chosen_ticket = next((t for t in tickets if t.ticket_id == chosen_id), None)
    if chosen_ticket:
        with st.container():
            st.markdown(f"### Ticket Details: `{chosen_ticket.ticket_id}`")
            d1, d2, d3, d4 = st.columns(4)
            d1.markdown(f"**Customer:** {chosen_ticket.customer.name if chosen_ticket.customer else 'N/A'}")
            d2.markdown(f"**Category:** {chosen_ticket.category}")
            d3.markdown(f"**Severity:** `{chosen_ticket.severity}`")
            d4.markdown(f"**Status:** {'🟢 Resolved' if chosen_ticket.status == 'Resolved' else '🟡 Open'}")

            st.info(f"**Original Issue:** {chosen_ticket.issue}")

            # Messages thread
            messages = MessageRepository.get_by_ticket(chosen_ticket.ticket_id)
            if messages:
                st.markdown("#### 💬 Conversation Thread")
                for m in messages:
                    is_user = m.sender == "customer"
                    with st.chat_message(name="user" if is_user else "assistant"):
                        st.markdown(f"**{m.sender.title()}** ({m.timestamp.strftime('%Y-%m-%d %H:%M') if m.timestamp else ''}):")
                        st.write(m.message)

            # Resolution Record
            res = ResolutionService.get_by_ticket(chosen_ticket.ticket_id)
            if res:
                st.markdown("#### ✅ Stored Resolution")
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown(f"**Identified Root Cause:**\n`{res.root_cause}`")
                    st.markdown(f"**Troubleshooting Steps:**\n{res.troubleshooting_steps}")
                with r_col2:
                    st.markdown(f"**Applied Solution:**\n> {res.solution}")
                    st.markdown(f"**Resolution Time:** {res.resolution_time} minutes")
                    if res.customer_feedback:
                        st.markdown(f"**Customer Feedback:** *\"{res.customer_feedback}\"*")
