"""LLM Client supporting Groq, OpenAI, and resilient offline fallback.

Uses official SDKs for Groq (groq) and OpenAI (openai).
Never leaks secret keys in error messages.
"""
from typing import List, Dict, Any, Tuple, Optional
from utils.config import config
from utils.logging import logger

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMClient:
    """Configurable LLM client with multi-provider support."""

    def test_connection(self) -> Tuple[bool, str]:
        """Test current LLM connection safely."""
        provider = config.llm_provider
        api_key = config.llm_api_key

        if not api_key or not api_key.strip():
            return False, f"LLM_API_KEY is not configured for provider '{provider}'."

        try:
            if provider == "groq":
                if not GROQ_AVAILABLE:
                    return False, "Groq official SDK is not installed."
                client = Groq(api_key=api_key)
                # Quick lightweight test query
                client.chat.completions.create(
                    model=config.llm_model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=2,
                )
                return True, f"Successfully connected to Groq (Model: {config.llm_model})."

            elif provider == "openai":
                if not OPENAI_AVAILABLE:
                    return False, "OpenAI official SDK is not installed."
                client = OpenAI(
                    api_key=api_key,
                    base_url=config.llm_base_url or None,
                )
                client.chat.completions.create(
                    model=config.llm_model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=2,
                )
                return True, f"Successfully connected to OpenAI (Model: {config.llm_model})."

            elif provider == "mock":
                return True, "Mock LLM provider is active (Demo/Offline Mode)."

            else:
                return False, f"Unsupported LLM provider '{provider}'. Use 'groq' or 'openai'."

        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "authorization" in err.lower():
                err = "Invalid API Key or unauthorized access."
            return False, f"LLM Connection failed: {err}"

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """Generate response via configured LLM provider or fallback simulator."""
        provider = config.llm_provider
        api_key = config.llm_api_key

        if provider == "groq" and GROQ_AVAILABLE and api_key:
            try:
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=config.llm_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"Groq API call error: {str(e)}")

        elif provider == "openai" and OPENAI_AVAILABLE and api_key:
            try:
                client = OpenAI(api_key=api_key, base_url=config.llm_base_url or None)
                response = client.chat.completions.create(
                    model=config.llm_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI API call error: {str(e)}")

        # Intelligent Fallback Generator if no live key is set
        return self._generate_simulated_response(messages)

    def _generate_simulated_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Intelligent simulation used when live LLM keys are absent,
        strictly respecting whether Hindsight memory is present in context.
        """
        user_msg = messages[-1]["content"] if messages else ""

        has_memory = "RELEVANT HINDSIGHT MEMORY" in user_msg and "No relevant previous experience" not in user_msg

        if has_memory:
            return (
                "### Understanding of the Issue\n"
                "I analyzed your current issue against your customer profile and support history.\n\n"
                "### Relevant Previous Experience\n"
                "🧠 **Found matching past interaction in Hindsight Memory:**\n"
                "In your previous support interaction, an identical symptom was diagnosed as an upload/session parameter limit within your account configuration.\n\n"
                "### Recommended Next Step\n"
                "Based directly on the previous successful resolution, verify your account-level quotas and reduce the file size or increase session timeout before attempting full reset.\n\n"
                "### Explanation & Confidence\n"
                "**Relevance:** High (Verified past solution).\n"
                "Because your environment matches the earlier incident, applying this proven fix directly prevents redundant troubleshooting steps.\n\n"
                "### What to Try Next\n"
                "1. Apply the previously verified configuration adjustment.\n"
                "2. Retry the operation.\n"
                "3. Let us know below if this immediately resolves your issue."
            )
        else:
            return (
                "### Understanding of the Issue\n"
                "Thank you for reporting this issue. I have analyzed your problem description and environment.\n\n"
                "### Relevant Previous Experience\n"
                "ℹ️ **No relevant previous memory found in Hindsight.** Treating this as an initial incident.\n\n"
                "### Recommended Next Step\n"
                "We recommend beginning with standard diagnostic isolation: inspect system logs, verify network stability, and confirm input formats match specification.\n\n"
                "### Explanation & Confidence\n"
                "**Relevance:** Baseline standard troubleshooting protocol.\n"
                "Without historical precedents, standard isolation is the safest path to isolate client vs server faults.\n\n"
                "### What to Try Next\n"
                "1. Check the application error logs for explicit failure codes.\n"
                "2. Verify network connectivity and file permissions.\n"
                "3. Report back with any error codes so we can pin down the root cause and store the solution for future reference."
            )


llm_client = LLMClient()
