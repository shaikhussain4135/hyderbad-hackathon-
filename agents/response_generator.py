"""Response Generator and Context Builder for Customer Support Agent."""
from typing import Dict, Any, List, Optional
from llm.llm_client import llm_client
from utils.logging import logger


class ResponseGenerator:
    """Builds synthesized prompt context and generates reasoned support recommendations."""

    def build_prompt_context(
        self,
        customer_info: Dict[str, Any],
        issue_info: Dict[str, Any],
        memories: List[Dict[str, Any]],
    ) -> str:
        """Compose structured context combining customer environment, current ticket, and recalled memories."""
        cust_context = (
            f"Customer ID: {customer_info.get('customer_id', 'Unknown')}\n"
            f"Name: {customer_info.get('name', 'Valued Customer')}\n"
            f"Product: {customer_info.get('product', 'Cloud Application')}\n"
            f"Plan: {customer_info.get('plan', 'Standard')}\n"
            f"Customer Environment: {customer_info.get('environment', 'Unknown')}"
        )

        issue_context = (
            f"Ticket Issue: {issue_info.get('issue', '')}\n"
            f"Category: {issue_info.get('category', 'General')}\n"
            f"Severity: {issue_info.get('severity', 'Medium')}\n"
            f"Observed Symptoms: {issue_info.get('symptoms', 'None specified')}\n"
            f"Preliminary Context: {issue_info.get('possible_context', 'Standard triage')}"
        )

        if memories:
            memory_items = []
            for i, m in enumerate(memories, start=1):
                memory_items.append(
                    f"Memory [{i}]:\n"
                    f"  - Past Issue: {m.get('issue', '')}\n"
                    f"  - Past Root Cause: {m.get('root_cause', 'Not documented')}\n"
                    f"  - Past Troubleshooting: {m.get('troubleshooting_steps', 'Standard')}\n"
                    f"  - Successful Solution: {m.get('solution', 'N/A')}\n"
                    f"  - Past Outcome: {m.get('outcome', 'Resolved')}\n"
                    f"  - Past Environment: {m.get('environment', 'Unknown')}"
                )
            memory_context = "\n\n".join(memory_items)
        else:
            memory_context = "No relevant previous experience found in Hindsight memory bank."

        system_instructions = (
            "You are an expert AI Customer Support Engineer equipped with persistent Hindsight memory.\n\n"
            "BEHAVIORAL RULES:\n"
            "1. Use previous memory when relevant, but do NOT blindly trust memory if current symptoms conflict.\n"
            "2. Do not claim something happened if memory does not explicitly support it.\n"
            "3. Distinguish previous experience from current diagnosis.\n"
            "4. If memory exists, explain clearly why the previous solution is relevant and recommended.\n"
            "5. If NO memory exists, explicitly acknowledge that no relevant memory was found and provide safe, general troubleshooting.\n"
            "6. Provide safe, actionable troubleshooting guidance with concrete steps.\n\n"
            "FORMAT YOUR RESPONSE EXACTLY WITH THESE SECTIONS:\n"
            "### Understanding of the Issue\n"
            "<Brief summary of the customer's problem in relation to their environment>\n\n"
            "### Relevant Previous Experience\n"
            "<Summary of what Hindsight memory recalled, or state 'No relevant previous memory found'>\n\n"
            "### Recommended Next Step\n"
            "<The primary, highest-confidence action the customer should take first>\n\n"
            "### Explanation & Confidence\n"
            "<Why this action is recommended and relevance/confidence indication>\n\n"
            "### What to Try Next\n"
            "<Step-by-step numbered instructions for the customer>"
        )

        user_prompt = (
            f"=== CUSTOMER CONTEXT ===\n{cust_context}\n\n"
            f"=== CURRENT ISSUE ===\n{issue_context}\n\n"
            f"=== RELEVANT HINDSIGHT MEMORY ===\n{memory_context}\n\n"
            "Please generate the personalized support response according to the behavioral rules."
        )

        return system_instructions, user_prompt

    def generate_response(
        self,
        customer_info: Dict[str, Any],
        issue_info: Dict[str, Any],
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate structured AI support response."""
        system_instr, user_prompt = self.build_prompt_context(
            customer_info=customer_info,
            issue_info=issue_info,
            memories=memories,
        )

        messages = [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": user_prompt},
        ]

        raw_response = llm_client.generate(messages=messages, temperature=0.2)

        return {
            "content": raw_response,
            "has_memory": len(memories) > 0,
            "memories_count": len(memories),
            "system_prompt": system_instr,
            "user_prompt": user_prompt,
        }


response_generator = ResponseGenerator()
