"""Issue Analyzer module for structured problem extraction."""
import re
from typing import Dict, Any, Optional
from llm.llm_client import llm_client
from utils.logging import logger


class IssueAnalyzer:
    """Analyzes customer issue description to extract category, severity, symptoms, and context."""

    def analyze(self, issue_description: str, environment: str = "Unknown") -> Dict[str, Any]:
        """Analyze issue text and return structured diagnostic breakdown."""
        cleaned = issue_description.strip()

        # Heuristic baseline
        lower = cleaned.lower()
        category = "General / Other"
        severity = "Medium"
        symptoms = "User reported operational difficulty"
        possible_context = "System behavior requires standard diagnostic isolation"

        if any(w in lower for w in ["disconnect", "session", "timeout", "kick", "logout", "login"]):
            category = "Application / Session"
            symptoms = "Repeated disconnection or authentication expiration"
            possible_context = "Session timeout, token expiration, or network instability"
            severity = "Medium"
        elif any(w in lower for w in ["upload", "pdf", "file", "attach", "size", "limit", "format"]):
            category = "File Management / Upload"
            symptoms = "Upload failure or processing interruption"
            possible_context = "File size limits, quota thresholds, or unsupported MIME type"
            severity = "Medium"
        elif any(w in lower for w in ["crash", "500", "down", "fatal", "outage", "error code"]):
            category = "Infrastructure / Availability"
            symptoms = "System failure or unexpected service error"
            possible_context = "Server-side exception, resource exhaustion, or unhandled bug"
            severity = "High"
        elif any(w in lower for w in ["slow", "lag", "latency", "delay", "freeze"]):
            category = "Performance / Latency"
            symptoms = "Unusually slow response or interface freeze"
            possible_context = "High database query load, client memory leak, or network congestion"
            severity = "Low"
        elif any(w in lower for w in ["billing", "invoice", "payment", "subscription", "upgrade"]):
            category = "Account / Billing"
            symptoms = "Billing inquiry or account plan limitation"
            possible_context = "Subscription status, payment method failure, or tier boundary"
            severity = "Low"

        # Check explicit severity triggers
        if any(w in lower for w in ["urgent", "critical", "production down", "emergency", "blocking"]):
            severity = "Critical"
        elif any(w in lower for w in ["minor", "cosmetic", "trivial"]):
            severity = "Low"

        # Refine with LLM if configured
        prompt = (
            f"You are a technical support triage assistant. Analyze this customer ticket:\n"
            f"Issue: \"{cleaned}\"\n"
            f"Environment: {environment}\n\n"
            f"Respond with a brief 4-line summary:\n"
            f"Category: <category>\n"
            f"Severity: <Low/Medium/High/Critical>\n"
            f"Symptoms: <observable symptoms>\n"
            f"Possible Context: <potential technical angles without stating root cause without proof>"
        )

        try:
            # Only call if we have an active LLM key
            from utils.config import config
            if config.llm_api_key:
                resp = llm_client.generate([{"role": "user", "content": prompt}], temperature=0.1)
                lines = resp.strip().split("\n")
                for line in lines:
                    if line.lower().startswith("category:"):
                        category = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("severity:"):
                        sev = line.split(":", 1)[1].strip()
                        if sev in ["Low", "Medium", "High", "Critical"]:
                            severity = sev
                    elif line.lower().startswith("symptoms:"):
                        symptoms = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("possible context:"):
                        possible_context = line.split(":", 1)[1].strip()
        except Exception as e:
            logger.warning(f"Issue analyzer LLM refinement skipped: {str(e)}")

        return {
            "summary": cleaned[:120] + ("..." if len(cleaned) > 120 else ""),
            "category": category,
            "severity": severity,
            "symptoms": symptoms,
            "possible_context": possible_context,
        }


issue_analyzer = IssueAnalyzer()
