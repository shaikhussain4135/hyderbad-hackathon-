"""Tests for database models, repositories, and schema creation."""
import pytest
from database.database import init_db, test_db_connection as check_db_conn, get_connection_info
from database.repositories import (
    CustomerRepository,
    TicketRepository,
    MessageRepository,
    ResolutionRepository,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_customer_creation_and_retrieval():
    cust = CustomerRepository.create(
        customer_id="test_cust_1",
        name="Test User",
        email="test.user@example.com",
        product="Cloud Service",
        plan="Pro",
        environment="macOS + Safari",
    )
    assert cust is not None
    assert cust.name == "Test User"

    fetched = CustomerRepository.get_by_id("test_cust_1")
    assert fetched is not None
    assert fetched.email == "test.user@example.com"


def test_ticket_lifecycle():
    import uuid
    uid = uuid.uuid4().hex[:6]
    cust = CustomerRepository.create(
        customer_id=f"test_cust_{uid}",
        name=f"Test User {uid}",
        email=f"user_{uid}@example.com",
        product="Platform",
        plan="Standard",
        environment="Windows 11",
    )
    t_id = f"TCK-TEST-{uid}"
    ticket = TicketRepository.create(
        ticket_id=t_id,
        customer_id=cust.customer_id,
        issue="Test Issue Description",
        category="General",
        severity="High",
        status="Open",
    )
    assert ticket.ticket_id == t_id
    assert ticket.status == "Open"

    # Add message
    msg = MessageRepository.create(
        message_id=f"msg_test_{uid}",
        ticket_id=ticket.ticket_id,
        sender="customer",
        message="Need urgent help",
    )
    assert msg.message == "Need urgent help"

    # Add resolution
    res = ResolutionRepository.create(
        resolution_id=f"res_test_{uid}",
        ticket_id=ticket.ticket_id,
        root_cause="Test cause",
        troubleshooting_steps="Steps taken",
        solution="Resolved with patch",
        outcome="Successfully resolved",
        resolution_time=10,
        customer_feedback="Great work",
    )
    assert res.solution == "Resolved with patch"

    # Update status
    updated = TicketRepository.update_status(ticket.ticket_id, "Resolved")
    assert updated is True
    refreshed = TicketRepository.get_by_id(ticket.ticket_id)
    assert refreshed.status == "Resolved"


def test_connection_info():
    dialect, is_neon = get_connection_info()
    assert dialect in ["Neon PostgreSQL", "Local SQLite (Configurable to Neon)"]
