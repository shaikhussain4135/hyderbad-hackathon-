"""Authentication and Login Page for Customer Support Memory Agent."""
import streamlit as st

# Pre-configured demo accounts for hackathon evaluation
DEMO_ACCOUNTS = {
    "admin": {
        "password": "admin123",
        "name": "Sarah Jenkins",
        "role": "Lead Support Architect",
        "avatar": "🛡️",
    },
    "agent": {
        "password": "support123",
        "name": "David Miller",
        "role": "Tier-2 Technical Specialist",
        "avatar": "🎧",
    },
    "judge": {
        "password": "hackathon2026",
        "name": "Hackathon Evaluator",
        "role": "VIP Reviewer",
        "avatar": "⭐",
    },
}


def render_login_page():
    """Render the centralized authentication portal."""
    st.markdown(
        """
        <style>
        .login-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 2.5rem;
            max-width: 500px;
            margin: 2rem auto;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .login-title {
            color: #f8fafc;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div class="login-card">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🧠</div>
                <div class="login-title">Customer Support Memory Agent</div>
                <div class="login-subtitle">Persistent Experience AI & Triage Console</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            st.markdown("### 🔐 Staff & Evaluator Login")
            username = st.text_input("Username / Agent ID", placeholder="admin, agent, or judge")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

            if submit:
                user_clean = username.strip().lower()
                if user_clean in DEMO_ACCOUNTS and DEMO_ACCOUNTS[user_clean]["password"] == password.strip():
                    user_data = DEMO_ACCOUNTS[user_clean]
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "username": user_clean,
                        "name": user_data["name"],
                        "role": user_data["role"],
                        "avatar": user_data["avatar"],
                    }
                    st.success(f"Welcome back, {user_data['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use one of the Quick Demo buttons below or enter valid credentials.")

        st.divider()

        # One-Click Demo Logins for Hackathon Evaluators
        st.markdown("#### ⚡ Quick Demo Logins (One-Click)")
        st.caption("Convenient shortcuts for instant evaluation without typing:")

        q_col1, q_col2, q_col3 = st.columns(3)

        if q_col1.button("👑 Admin Login", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "username": "admin",
                "name": "Sarah Jenkins",
                "role": "Lead Support Architect",
                "avatar": "🛡️",
            }
            st.rerun()

        if q_col2.button("🎧 Agent Login", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "username": "agent",
                "name": "David Miller",
                "role": "Tier-2 Technical Specialist",
                "avatar": "🎧",
            }
            st.rerun()

        if q_col3.button("⭐ Judge Login", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "username": "judge",
                "name": "Hackathon Evaluator",
                "role": "VIP Reviewer",
                "avatar": "⭐",
            }
            st.rerun()

        with st.expander("ℹ️ View Demo Credentials"):
            st.markdown(
                """
                - **Admin:** `admin` / `admin123`
                - **Support Agent:** `agent` / `support123`
                - **Judge:** `judge` / `hackathon2026`
                """
            )
