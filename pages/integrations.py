"""Integration and Connection Setup Page."""
import streamlit as st
from utils.config import config, mask_secret
from database.database import test_db_connection, get_connection_info
from memory.hindsight_manager import memory_manager
from llm.llm_client import llm_client


def render_integrations_page():
    st.title("🔌 Integration & Connection Setup")
    st.markdown(
        "Verify, test, and safely configure the core external services: "
        "**Hindsight Memory**, **Neon PostgreSQL Database**, and **LLM Provider**."
    )

    # 1. Connection Status Overview Cards
    col1, col2, col3 = st.columns(3)

    # Database Status
    with col1:
        st.subheader("Neon PostgreSQL")
        backend_name, is_neon = get_connection_info()
        if is_neon:
            st.success("🟢 Connected to Neon DB")
        else:
            st.info(f"🔵 Active: {backend_name}")
        st.caption(f"Target: `{mask_secret(config.database_url, 8)}`")

    # Hindsight Status
    with col2:
        st.subheader("Hindsight Memory")
        is_hindsight_live, h_msg = memory_manager.test_connection()
        if is_hindsight_live:
            st.success("🟢 Connected to Server")
        else:
            st.warning("🟠 Local Bank Active")
        st.caption(f"Endpoint: `{config.hindsight_url or 'Not Set'}`")

    # LLM Status
    with col3:
        st.subheader("LLM Provider")
        llm_ok, _ = llm_client.test_connection()
        if llm_ok:
            st.success(f"🟢 Connected ({config.llm_provider})")
        else:
            st.info("🔵 Active: Local Reasoning Simulator")
        st.caption(f"Model: `{config.llm_model}`")

    st.divider()

    # 2. Test Connection Buttons
    st.subheader("🧪 Diagnostics & Health Tests")
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)

    test_hs = bcol1.button("Test Hindsight", use_container_width=True)
    test_db = bcol2.button("Test Database", use_container_width=True)
    test_llm = bcol3.button("Test LLM", use_container_width=True)
    test_all = bcol4.button("Test All Services", type="primary", use_container_width=True)

    if test_hs or test_all:
        with st.spinner("Testing Hindsight Memory connection..."):
            ok, msg = memory_manager.test_connection()
            if ok:
                st.success(f"✅ Hindsight: {msg}")
            else:
                st.error(f"❌ Hindsight: {msg}")
                st.info("ℹ️ Tip: Ensure Hindsight server is running (e.g. `docker run -p 8888:8888 vectorizeio/hindsight`) or configure cloud URL.")

    if test_db or test_all:
        with st.spinner("Testing Neon PostgreSQL connection..."):
            ok, msg = test_db_connection()
            if ok:
                st.success(f"✅ Database: {msg}")
            else:
                st.error(f"❌ Database: {msg}")
                st.info("ℹ️ Tip: Set `DATABASE_URL=postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require` from your Neon console.")

    if test_llm or test_all:
        with st.spinner("Testing LLM Provider connection..."):
            ok, msg = llm_client.test_connection()
            if ok:
                st.success(f"✅ LLM: {msg}")
            else:
                st.error(f"❌ LLM: {msg}")
                st.info("ℹ️ Tip: Provide a valid Groq (`gsk_...`) or OpenAI API key below.")

    st.divider()

    # 3. Secure Configuration Editor
    st.subheader("⚙️ Local Service Credentials")
    st.markdown(
        "You can enter and update your credentials directly below. "
        "They are saved safely to your local environment and applied immediately without restarting the app."
    )

    with st.form("config_form"):
        st.markdown("#### 1. Hindsight Memory Server")
        st.caption("🔗 [Hindsight GitHub & Docs](https://github.com/vectorize-io/hindsight) | Default local endpoint: `http://localhost:8888`")
        f_hindsight_url = st.text_input(
            "Hindsight Endpoint URL",
            value=config.hindsight_url,
            placeholder="http://localhost:8888 or cloud endpoint"
        )
        f_hindsight_key = st.text_input(
            "Hindsight API Key (Optional for local)",
            value=config.hindsight_api_key or "",
            type="password",
            placeholder="Enter Hindsight API key if using cloud"
        )

        st.markdown("#### 2. Neon PostgreSQL Database")
        st.caption("🔗 [Get Neon Database Connection String](https://console.neon.tech) — Format: `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`")
        f_db_url = st.text_input(
            "Neon Connection String (DATABASE_URL)",
            value=config.database_url or "",
            type="password",
            placeholder="postgresql://user:password@ep-something.us-east-2.aws.neon.tech/neondb?sslmode=require"
        )

        st.markdown("#### 3. LLM Reasoning Engine")
        st.caption("🔗 [Get Free Groq API Key](https://console.groq.com/keys) | [OpenAI API Keys](https://platform.openai.com/api-keys)")
        provider_options = ["groq", "openai", "mock"]
        current_idx = provider_options.index(config.llm_provider) if config.llm_provider in provider_options else 0
        f_provider = st.selectbox("LLM Provider", options=provider_options, index=current_idx)

        f_llm_key = st.text_input(
            f"{f_provider.title()} API Key",
            value=config.llm_api_key or "",
            type="password",
            placeholder=f"Enter {f_provider} API key (e.g. gsk_... for Groq)"
        )

        default_model = "llama-3.3-70b-versatile" if f_provider == "groq" else "gpt-4o-mini"
        f_llm_model = st.text_input("LLM Model Name", value=config.llm_model or default_model)

        f_base_url = st.text_input(
            "Custom LLM Base URL (Optional / Self-hosted)",
            value=config.llm_base_url or "",
            placeholder="https://api.groq.com/openai/v1 or custom proxy"
        )

        submitted = st.form_submit_button("💾 Save & Apply Configuration", use_container_width=True)

        if submitted:
            config.update_and_save(
                hindsight_url=f_hindsight_url,
                hindsight_api_key=f_hindsight_key,
                database_url=f_db_url,
                llm_provider=f_provider,
                llm_api_key=f_llm_key,
                llm_model=f_llm_model,
                llm_base_url=f_base_url,
            )
            st.success("✅ Configuration saved and reloaded! Run the diagnostic tests above to verify.")
            st.rerun()
