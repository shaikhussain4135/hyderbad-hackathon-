"""Memory Explorer Page for Hindsight Persistent Memory Visualization."""
import streamlit as st
import json
from memory.hindsight_manager import memory_manager
from services.customer_service import CustomerService


def render_memory_explorer_page():
    st.title("🧠 Hindsight Memory Explorer")
    st.markdown(
        "Inspect persistent AI memory banks, examine learned support resolutions, "
        "and test semantic recall in real time."
    )

    # 1. Visual Architecture Flow Diagram
    with st.container():
        st.markdown(
            """
            <div style="background-color: #1e293b; padding: 18px; border-radius: 10px; border-left: 5px solid #38bdf8; margin-bottom: 20px;">
                <h4 style="color: #f8fafc; margin-top: 0;">⚡ How Hindsight Persistent Memory Works in Customer Support</h4>
                <div style="display: flex; justify-content: space-between; align-items: center; text-align: center; color: #cbd5e1; font-weight: 500; font-size: 14px;">
                    <div>📋 <b>Current Issue</b><br><small>Ticket submitted</small></div>
                    <div style="font-size: 20px; color: #38bdf8;">➔</div>
                    <div>🧠 <b>Hindsight Retrieval</b><br><small>Semantic TEMPR search</small></div>
                    <div style="font-size: 20px; color: #38bdf8;">➔</div>
                    <div>🤖 <b>LLM Reasoning</b><br><small>Context + past fix</small></div>
                    <div style="font-size: 20px; color: #38bdf8;">➔</div>
                    <div>🎯 <b>Personalized Fix</b><br><small>Zero redundant steps</small></div>
                    <div style="font-size: 20px; color: #38bdf8;">➔</div>
                    <div>💾 <b>Hindsight Retain</b><br><small>Stores new learnings</small></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Interactive Recall Tester
    st.subheader("🔎 Live Memory Recall Simulator")
    st.caption("Test how Hindsight surfaces relevant past experiences given a simulated customer query.")

    customers = CustomerService.list_all()
    q_col1, q_col2 = st.columns([1, 2])

    with q_col1:
        cust_choices = {"All Customers": None}
        for c in customers:
            cust_choices[f"{c.name} ({c.customer_id})"] = c.customer_id
        selected_cust_label = st.selectbox("Customer Filter", options=list(cust_choices.keys()))
        filter_cust_id = cust_choices[selected_cust_label]

    with q_col2:
        test_query = st.text_input(
            "Enter Test Query or Symptom",
            value="PDF upload fails when sending large file",
            placeholder="e.g. dashboard disconnects, session logout, pdf size error"
        )

    if st.button("🔍 Search Hindsight Memory", type="primary"):
        with st.spinner("Executing semantic recall across memory banks..."):
            recalled = memory_manager.recall_experiences(
                customer_id=filter_cust_id or "",
                query=test_query,
                top_k=5
            )

            if recalled:
                st.success(f"Recalled {len(recalled)} matching memory experience(s)!")
                for i, r in enumerate(recalled, 1):
                    with st.expander(f"Memory Hit #{i}: {r.get('issue')} (Match: {int(r.get('score', 0.9)*100)}%)", expanded=True):
                        st.markdown(f"**Identified Root Cause:** `{r.get('root_cause')}`")
                        st.markdown(f"**Verified Solution:** {r.get('solution')}")
                        st.markdown(f"**Outcome:** `{r.get('outcome')}`")
                        st.caption(f"Memory ID: `{r.get('memory_id')}` | Source: `{r.get('source')}`")
            else:
                st.warning("No relevant memory found matching this query in the memory bank.")

    st.divider()

    # 3. All Stored Memories Catalog
    all_memories = memory_manager.list_all_memories(customer_id=filter_cust_id)

    st.subheader(f"📚 Stored Memory Units ({len(all_memories)})")
    st.caption("Persistent records stored in Hindsight memory banks.")

    if not all_memories:
        st.info("No memories stored yet. Run 'Seed Demo Data' on the Dashboard or resolve a ticket to retain memories.")
    else:
        for idx, mem in enumerate(all_memories, 1):
            with st.container():
                st.markdown(f"#### 🧠 Memory #{idx}: {mem.get('issue', 'Support Interaction')}")
                mcol1, mcol2 = st.columns(2)

                with mcol1:
                    st.markdown(f"**Customer ID:** `{mem.get('customer_id')}`")
                    st.markdown(f"**Ticket ID:** `{mem.get('ticket_id')}`")
                    st.markdown(f"**Category:** `{mem.get('category')}`")
                    st.markdown(f"**Environment:** {mem.get('environment')}")
                    st.markdown(f"**Created At:** {mem.get('timestamp')}")

                with mcol2:
                    st.markdown(f"**Root Cause:**\n`{mem.get('root_cause')}`")
                    st.markdown(f"**Troubleshooting:**\n{mem.get('troubleshooting_steps')}")
                    st.markdown(f"**Verified Solution:**\n> {mem.get('solution')}")
                    st.markdown(f"**Outcome:** ✅ `{mem.get('outcome')}`")
                    if mem.get("customer_feedback"):
                        st.markdown(f"**Customer Feedback:** *\"{mem.get('customer_feedback')}\"*")

                with st.expander("View Raw Memory Payload (JSON)"):
                    st.code(json.dumps(mem, indent=2), language="json")

                st.divider()
