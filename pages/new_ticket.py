"""New Support Ticket Page with AI Reasoning and Feedback Loop."""
import streamlit as st
from services.customer_service import CustomerService
from services.ticket_service import TicketService
from agents.support_agent import support_agent


def render_new_ticket_page():
    st.title("🎫 New Support Ticket")
    st.markdown("Submit a customer issue to trigger **AI Analysis**, **Hindsight Memory Retrieval**, and **Reasoned Recommendations**.")

    # Fetch existing customers or allow new customer creation
    customers = CustomerService.list_all()

    # Form: Ticket Submission
    with st.expander("📝 Ticket Submission Form", expanded="agent_result" not in st.session_state):
        col_c1, col_c2 = st.columns(2)

        customer_options = {c.name: c for c in customers}
        customer_options["➕ Add New Customer..."] = None

        with col_c1:
            selected_name = st.selectbox(
                "Select Customer",
                options=list(customer_options.keys()),
                index=0 if customers else None
            )

        selected_cust = customer_options.get(selected_name)

        if selected_cust is None:
            # New Customer inline inputs
            with col_c2:
                new_cust_name = st.text_input("Customer Name", value="Jane Doe")
            with col_c1:
                new_cust_email = st.text_input("Customer Email", value="jane.doe@example.com")
            with col_c2:
                product_val = st.text_input("Product Name", value="Cloud Platform Pro")
            with col_c1:
                plan_val = st.selectbox("Plan Tier", ["Standard", "Pro", "Enterprise"])
            with col_c2:
                env_val = st.text_input("Environment", value="Windows 11 + Chrome")
            effective_cust_id = f"cust_{new_cust_name.lower().replace(' ', '_')}"
        else:
            effective_cust_id = selected_cust.customer_id
            with col_c2:
                product_val = st.text_input("Product Name", value=selected_cust.product)
            with col_c1:
                env_val = st.text_input("Environment", value=selected_cust.environment)
            with col_c2:
                plan_val = st.text_input("Plan Tier", value=selected_cust.plan, disabled=True)

        st.markdown("#### Issue Details")
        issue_text = st.text_area(
            "Customer Issue Description",
            height=120,
            placeholder="e.g. My PDF upload is failing again when submitting monthly files...",
            help="Type any real support problem or quick test scenario."
        )

        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            severity_choice = st.selectbox("Reported Severity", ["Low", "Medium", "High", "Critical"], index=1)
        with col_s2:
            st.caption("⚡ Quick Demo Presets:")
            p_col1, p_col2, p_col3 = st.columns(3)
            if p_col1.button("Main Demo 1 (PDF Upload)"):
                st.session_state["preset_issue"] = "My PDF upload is failing again."
                st.rerun()
            if p_col2.button("Main Demo 2 (Disconnect)"):
                st.session_state["preset_issue"] = "My dashboard keeps disconnecting every 10 minutes."
                st.rerun()
            if p_col3.button("Scenario 3 (New / No Memory)"):
                st.session_state["preset_issue"] = "Receiving HTTP 403 Forbidden on our custom webhook subscription endpoint."
                st.rerun()

        if "preset_issue" in st.session_state and not issue_text:
            issue_text = st.session_state.pop("preset_issue")

        submit_btn = st.button("🚀 Analyze Issue & Consult Hindsight Memory", type="primary", use_container_width=True)

    if submit_btn:
        if not issue_text.strip():
            st.error("Please provide an issue description.")
            return

        with st.spinner("Analyzing issue, searching Hindsight memory, and synthesizing recommendation..."):
            # Ensure customer is recorded
            if selected_cust is None:
                selected_cust = CustomerService.get_or_create(
                    customer_id=effective_cust_id,
                    name=new_cust_name,
                    email=new_cust_email,
                    product=product_val,
                    plan=plan_val,
                    environment=env_val,
                )

            # Create ticket record in Neon / SQL database
            ticket = TicketService.create_ticket(
                customer_id=selected_cust.customer_id,
                issue=issue_text.strip(),
                category="Analyzing...",
                severity=severity_choice,
            )

            # Run full Agent orchestration
            result = support_agent.process_ticket(
                customer_id=selected_cust.customer_id,
                issue_description=issue_text.strip(),
                environment=env_val,
                severity_override=severity_choice,
            )

            # Store in session state for feedback interaction
            st.session_state["active_ticket"] = ticket.to_dict()
            st.session_state["agent_result"] = result
            st.session_state["ticket_resolved"] = False

    # Render Results if available in session
    if "agent_result" in st.session_state:
        res = st.session_state["agent_result"]
        t_data = st.session_state.get("active_ticket", {})

        st.divider()
        st.subheader(f"📌 Ticket #{t_data.get('ticket_id', 'TCK-NEW')} Triage Analysis")

        # 1. CURRENT ISSUE SECTION
        with st.container():
            st.markdown("### 📋 Current Issue")
            ic1, ic2, ic3, ic4 = st.columns(4)
            ic1.markdown(f"**Customer:** {res['customer'].get('name')}")
            ic2.markdown(f"**Product:** {res['customer'].get('product')}")
            ic3.markdown(f"**Environment:** {res['customer'].get('environment')}")
            ic4.markdown(f"**Severity:** `{res['analysis'].get('severity')}`")
            st.info(f"**Issue Description:** {t_data.get('issue')}")

        st.divider()

        # 2. AI ANALYSIS SECTION
        with st.container():
            st.markdown("### 🔍 AI Analysis")
            ac1, ac2, ac3 = st.columns(3)
            ac1.markdown(f"**Issue Category:**\n`{res['analysis'].get('category')}`")
            ac2.markdown(f"**Identified Symptoms:**\n{res['analysis'].get('symptoms')}")
            ac3.markdown(f"**Possible Angles:**\n{res['analysis'].get('possible_context')}")

        st.divider()

        # 3. HINDSIGHT MEMORY SECTION (Crucial visual distinction)
        st.markdown("### 🧠 Hindsight Memory")
        if res["has_memory"]:
            st.success(f"**MEMORY FOUND:** {len(res['memories'])} relevant previous interaction(s) recalled!")
            for idx, mem in enumerate(res["memories"], start=1):
                with st.expander(f"Recall #{idx}: {mem.get('issue')} (Relevance: {int(mem.get('score', 0.9)*100)}%)", expanded=True):
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        st.markdown(f"**Previous Issue:** {mem.get('issue')}")
                        st.markdown(f"**Previous Root Cause:** `{mem.get('root_cause')}`")
                        st.markdown(f"**Environment:** {mem.get('environment')}")
                    with mc2:
                        st.markdown(f"**Previous Successful Solution:**\n> {mem.get('solution')}")
                        st.markdown(f"**Previous Outcome:** ✅ `{mem.get('outcome')}`")
                        st.caption(f"Source: {mem.get('source')}")
        else:
            st.info("ℹ️ **No relevant previous memory found in Hindsight.**\nAgent will formulate a standard diagnostic resolution plan.")

        st.divider()

        # 4. AI RECOMMENDATION SECTION
        st.markdown("### 🤖 AI Recommendation")
        st.markdown(res["recommendation"])

        st.divider()

        # 5. FEEDBACK LOOP SECTION
        st.subheader("🔄 Customer Feedback & Resolution Loop")

        if st.session_state.get("ticket_resolved"):
            st.success("✅ **Ticket has been resolved and new experience has been retained into Hindsight memory!**")
            if st.button("Start Another Ticket"):
                st.session_state.pop("agent_result", None)
                st.session_state.pop("active_ticket", None)
                st.session_state.pop("ticket_resolved", None)
                st.rerun()
        else:
            st.markdown("**Did this recommendation resolve the customer's issue?**")
            f_col1, f_col2 = st.columns(2)

            with f_col1:
                yes_btn = st.button("✅ YES — RESOLVED", type="primary", use_container_width=True)
            with f_col2:
                no_btn = st.button("❌ NO — STILL NOT RESOLVED", use_container_width=True)

            if yes_btn:
                st.session_state["show_resolution_dialog"] = True

            if no_btn:
                st.warning(
                    "⚠️ Marked as Unresolved. The agent will continue troubleshooting without saving false memory.\n"
                    "Please ask the customer for additional error traces or system logs."
                )

            # Resolution capture modal/form
            if st.session_state.get("show_resolution_dialog"):
                with st.form("resolution_form"):
                    st.markdown("#### 📝 Record Resolution & Retain into Hindsight")
                    st.caption("Storing verified solutions enables the agent to provide instant personalized help when similar issues occur in the future.")

                    default_cause = res["memories"][0].get("root_cause") if res["has_memory"] else "Configuration / Limit parameter"
                    default_sol = res["memories"][0].get("solution") if res["has_memory"] else "Adjusted setting to within allowable threshold"

                    f_root_cause = st.text_input("Root Cause", value=default_cause)
                    f_steps = st.text_input("Troubleshooting Steps Taken", value="Verified settings and validated operation.")
                    f_solution = f_solution = st.text_area("Solution Used", value=default_sol)
                    f_time = st.number_input("Resolution Time (minutes)", min_value=1, max_value=300, value=15)
                    f_feedback = st.text_input("Customer Feedback", value="Resolved the issue quickly and accurately!")

                    save_btn = st.form_submit_button("💾 Save Resolution & Retain Experience", use_container_width=True)

                    if save_btn:
                        support_agent.resolve_ticket_and_retain_memory(
                            ticket_id=t_data["ticket_id"],
                            customer_id=t_data["customer_id"],
                            issue=t_data["issue"],
                            category=res["analysis"]["category"],
                            root_cause=f_root_cause,
                            troubleshooting_steps=f_steps,
                            solution=f_solution,
                            outcome="Successfully resolved",
                            resolution_time=int(f_time),
                            environment=res["customer"].get("environment", "Unknown"),
                            customer_feedback=f_feedback,
                        )
                        st.session_state["ticket_resolved"] = True
                        st.session_state["show_resolution_dialog"] = False
                        st.rerun()
