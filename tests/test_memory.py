"""Tests for Hindsight memory manager: retain, recall, and no-memory scenarios."""
import pytest
from memory.hindsight_manager import memory_manager


def test_retain_and_recall_experience():
    # Retain a specific experience
    record = memory_manager.retain_experience(
        customer_id="cust_test_memory",
        ticket_id="TCK-MEM-001",
        issue="Database connection timeout on query execution",
        category="Database / Sync",
        root_cause="Connection pool max size reached",
        troubleshooting_steps="Monitored active connections and inspected pool settings",
        solution="Increased pool_size from 5 to 20 and pool_recycle to 300",
        outcome="Successfully resolved",
        environment="Linux Docker",
        customer_feedback="Fixed all timeouts immediately",
    )
    assert record["memory_id"] is not None

    # Recall using similar terms
    recalled = memory_manager.recall_experiences(
        customer_id="cust_test_memory",
        query="database timeout connection pool",
        top_k=3,
    )
    assert len(recalled) > 0
    assert "connection pool" in recalled[0]["solution"].lower() or "timeout" in recalled[0]["issue"].lower()


def test_no_memory_scenario():
    # Query for a brand new customer and unrelated issue
    recalled = memory_manager.recall_experiences(
        customer_id="cust_brand_new_unseen",
        query="Quantum entanglement cryptographic key failure",
        top_k=3,
    )
    assert len(recalled) == 0


def test_list_all_memories():
    mems = memory_manager.list_all_memories()
    assert isinstance(mems, list)
