"""Central CustomerSupportAgent Orchestrator.

Orchestrates the entire lifecycle:
Issue Analysis -> Hindsight Memory Retrieval -> Context Building -> LLM Reasoning -> Solution Generation -> Feedback -> Memory Retain.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from agents.issue_analyzer import issue_analyzer
from agents.response_generator import response_generator
from memory.hindsight_manager import memory_manager
from database.repositories import CustomerRepository, TicketRepository, ResolutionRepository, MessageRepository
from utils.logging import logger


class CustomerSupportAgent:
    """Central orchestrator for AI-powered, memory-enhanced support assistance."""

    def __init__(self):
        self.analyzer = issue_analyzer
        self.generator = response_generator
        self.memory = memory_manager

    def process_ticket(
        self,
        customer_id: str,
        issue_description: str,
        environment: Optional[str] = None,
        severity_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full diagnostic and recommendation pipeline.
        1. Look up customer context.
        2. Analyze issue symptoms and category.
        3. Recall previous experiences from Hindsight.
        4. Synthesize personalized recommendation via LLM.
        """
        # Step 1: Customer Context
        customer = CustomerRepository.get_by_id(customer_id)
        if customer:
            customer_data = customer.to_dict()
        else:
            customer_data = {
                "customer_id": customer_id,
                "name": "Customer",
                "product": "Cloud Service",
                "plan": "Standard",
                "environment": environment or "Production",
            }

        effective_env = environment or customer_data.get("environment", "Unknown")

        # Step 2: Issue Analysis
        analysis = self.analyzer.analyze(issue_description=issue_description, environment=effective_env)
        if severity_override and severity_override in ["Low", "Medium", "High", "Critical"]:
            analysis["severity"] = severity_override

        # Step 3: Search Hindsight Memory
        recalled_memories = self.memory.recall_experiences(
            customer_id=customer_id,
            query=f"{issue_description} {analysis['category']}",
            category=analysis["category"],
            top_k=3,
        )

        has_memory = len(recalled_memories) > 0

        # Step 4: LLM Reasoning & Response Generation
        issue_info = {
            "issue": issue_description,
            "category": analysis["category"],
            "severity": analysis["severity"],
            "symptoms": analysis["symptoms"],
            "possible_context": analysis["possible_context"],
        }

        generated = self.generator.generate_response(
            customer_info=customer_data,
            issue_info=issue_info,
            memories=recalled_memories,
        )

        return {
            "customer": customer_data,
            "analysis": analysis,
            "memories": recalled_memories,
            "has_memory": has_memory,
            "recommendation": generated["content"],
            "raw_context": {
                "system_prompt": generated["system_prompt"],
                "user_prompt": generated["user_prompt"],
            }
        }

    def resolve_ticket_and_retain_memory(
        self,
        ticket_id: str,
        customer_id: str,
        issue: str,
        category: str,
        root_cause: str,
        troubleshooting_steps: str,
        solution: str,
        outcome: str = "Resolved",
        resolution_time: int = 15,
        environment: str = "Unknown",
        customer_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record resolution in database and retain experience into persistent Hindsight memory.
        """
        resolution_id = f"res_{uuid.uuid4().hex[:10]}"

        # 1. Update ticket in Neon DB
        TicketRepository.update_status(ticket_id=ticket_id, status="Resolved", resolved_at=datetime.now(timezone.utc))

        # 2. Save structured resolution in Neon DB
        res_record = ResolutionRepository.create(
            resolution_id=resolution_id,
            ticket_id=ticket_id,
            root_cause=root_cause,
            troubleshooting_steps=troubleshooting_steps,
            solution=solution,
            outcome=outcome,
            resolution_time=resolution_time,
            customer_feedback=customer_feedback,
        )

        # 3. Retain experience in Hindsight persistent memory
        memory_record = self.memory.retain_experience(
            customer_id=customer_id,
            ticket_id=ticket_id,
            issue=issue,
            category=category,
            root_cause=root_cause,
            troubleshooting_steps=troubleshooting_steps,
            solution=solution,
            outcome=outcome,
            environment=environment,
            customer_feedback=customer_feedback,
        )

        logger.info(f"Ticket {ticket_id} resolved and experience retained into Hindsight memory.")

        return {
            "resolution": res_record.to_dict(),
            "memory": memory_record,
            "status": "success",
            "message": "Resolution saved and experience learned into Hindsight memory."
        }


support_agent = CustomerSupportAgent()
