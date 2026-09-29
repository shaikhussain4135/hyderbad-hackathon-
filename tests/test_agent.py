"""Tests for AI Agent, Issue Analyzer, Response Generator, and Full End-to-End Learning Flow."""
import pytest
from agents.issue_analyzer import issue_analyzer
from agents.response_generator import response_generator
from agents.support_agent import support_agent
from database.repositories import CustomerRepository, TicketRepository


def test_issue_analyzer():
    res = issue_analyzer.analyze("My dashboard disconnects every 10 minutes", "macOS")
    assert res["category"] == "Application / Session"
    assert "disconnect" in res["symptoms"].lower()

    res2 = issue_analyzer.analyze("PDF upload size exceeds limit", "Windows 11")
    assert res2["category"] == "File Management / Upload"


def test_response_generator_prompt_composition():
    cust_info = {
        "customer_id": "cust_demo",
        "name": "Demo User",
        "product": "Cloud App",
        "plan": "Pro",
        "environment": "Windows 11",
    }
    issue_info = {
        "issue": "Cannot upload PDF",
        "category": "File Management / Upload",
        "severity": "Medium",
        "symptoms": "Upload fails",
        "possible_context": "File size limit",
    }
    memories = [
        {
            "issue": "PDF upload failed",
            "root_cause": "File size limit",
            "solution": "Compress PDF",
            "outcome": "Resolved",
            "environment": "Windows 11",
        }
    ]

    resp = response_generator.generate_response(cust_info, issue_info, memories)
    assert resp["has_memory"] is True
    assert "Understanding of the Issue" in resp["content"]


def test_end_to_end_memory_learning_loop():
    """
    End-to-End workflow test:
    1. New customer submits an issue without prior memory
    2. Agent diagnoses with baseline protocol (has_memory=False)
    3. Issue resolved & solution retained in Hindsight
    4. Same customer submits similar issue
    5. Agent recalls previous solution from Hindsight (has_memory=True)
    """
    cust_id = "cust_e2e_learner"
    CustomerRepository.create(
        customer_id=cust_id,
        name="E2E Learner",
        email="learner@example.com",
        product="Data Lake Engine",
        plan="Enterprise",
        environment="Ubuntu 22.04 LTS",
    )

    # 1. First interaction: Fresh issue
    first_issue = "Query fails with timeout after 30 seconds"
    res1 = support_agent.process_ticket(customer_id=cust_id, issue_description=first_issue)
    assert res1["has_memory"] is False

    # 2. Resolve ticket & learn experience into Hindsight
    t1 = TicketRepository.create(
        ticket_id="TCK-E2E-01",
        customer_id=cust_id,
        issue=first_issue,
        category=res1["analysis"]["category"],
    )

    support_agent.resolve_ticket_and_retain_memory(
        ticket_id=t1.ticket_id,
        customer_id=cust_id,
        issue=first_issue,
        category=res1["analysis"]["category"],
        root_cause="Query statement timeout exceeded 30s threshold on heavy joins",
        troubleshooting_steps="Analyzed EXPLAIN query plan and statement_timeout setting",
        solution="Increased statement_timeout to 120s and added btree index on join key",
        outcome="Successfully resolved",
        resolution_time=20,
        environment="Ubuntu 22.04 LTS",
        customer_feedback="Query now finishes in 4s",
    )

    # 3. Second interaction: Similar issue submitted
    second_issue = "Query fails with timeout again on new reports"
    res2 = support_agent.process_ticket(customer_id=cust_id, issue_description=second_issue)

    # Agent should recall previous experience!
    assert res2["has_memory"] is True
    assert len(res2["memories"]) > 0
    assert "statement_timeout" in res2["memories"][0]["root_cause"] or "statement_timeout" in res2["memories"][0]["solution"]
