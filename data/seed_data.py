"""Synthetic seed data loader for hackathon demonstration.

Initializes realistic customers, tickets, resolutions, and Hindsight persistent memories.
Contains NO real customer data.
"""
from datetime import datetime, timezone, timedelta
from database.database import init_db
from database.repositories import (
    CustomerRepository,
    TicketRepository,
    ResolutionRepository,
    MessageRepository
)
from memory.hindsight_manager import memory_manager
from utils.logging import logger


def seed_database_and_memory(clear_existing: bool = False):
    """Seed demo customers, past resolved tickets, and Hindsight memory."""
    init_db()

    logger.info("Starting demo data seeding...")

    # --- Customer 1: John Smith (Main Demo Scenario) ---
    cust1 = CustomerRepository.create(
        customer_id="cust_john_smith",
        name="John Smith",
        email="john.smith@demo-acme-corp.com",
        product="Document Cloud Enterprise",
        plan="Enterprise",
        environment="Windows 11 + Chrome 122",
    )

    # Historical Resolved Ticket for John Smith
    t1_id = "TCK-PDF-001"
    t1 = TicketRepository.get_by_id(t1_id)
    if not t1:
        TicketRepository.create(
            ticket_id=t1_id,
            customer_id=cust1.customer_id,
            issue="PDF upload failure when processing quarterly reports",
            category="File Management / Upload",
            severity="Medium",
            status="Resolved",
        )
        resolved_time = datetime.now(timezone.utc) - timedelta(days=5)
        TicketRepository.update_status(t1_id, "Resolved", resolved_at=resolved_time)

        MessageRepository.create(
            message_id="msg_pdf_01",
            ticket_id=t1_id,
            sender="customer",
            message="Every time I try to upload my quarterly financial PDF report, the progress bar freezes and errors out.",
        )
        MessageRepository.create(
            message_id="msg_pdf_02",
            ticket_id=t1_id,
            sender="agent",
            message="We inspected the payload: your account upload threshold was capped at 25MB while the file was 32MB.",
        )

        ResolutionRepository.create(
            resolution_id="res_pdf_001",
            ticket_id=t1_id,
            root_cause="File size exceeded account upload quota limit (32MB payload vs 25MB ceiling)",
            troubleshooting_steps="Verified file byte size, checked tenant quota metrics, and confirmed account tier limits.",
            solution="Reduce file size / compress PDF or upgrade account upload quota limit.",
            outcome="Successfully resolved",
            resolution_time=12,
            customer_feedback="Compressing the PDF worked immediately. Thank you!",
        )

        # Retain into Hindsight persistent memory
        memory_manager.retain_experience(
            customer_id=cust1.customer_id,
            ticket_id=t1_id,
            issue="PDF upload failure when processing quarterly reports",
            category="File Management / Upload",
            root_cause="File size exceeded account upload quota limit (32MB payload vs 25MB ceiling)",
            troubleshooting_steps="Verified file byte size, checked tenant quota metrics, and confirmed account tier limits.",
            solution="Reduce file size / compress PDF or upgrade account upload quota limit.",
            outcome="Successfully resolved",
            environment="Windows 11 + Chrome 122",
            customer_feedback="Compressing the PDF worked immediately. Thank you!",
        )

    # --- Customer 2: Sarah Connor (Second Demo Scenario) ---
    cust2 = CustomerRepository.create(
        customer_id="cust_sarah_connor",
        name="Sarah Connor",
        email="sarah.connor@cyberdyne-defense.org",
        product="Operations Center Dashboard",
        plan="Pro",
        environment="macOS Sonoma 14.3 + Safari 17",
    )

    t2_id = "TCK-DASH-002"
    t2 = TicketRepository.get_by_id(t2_id)
    if not t2:
        TicketRepository.create(
            ticket_id=t2_id,
            customer_id=cust2.customer_id,
            issue="My dashboard disconnects every 10 minutes unexpectedly",
            category="Application / Session",
            severity="Medium",
            status="Resolved",
        )
        resolved_time2 = datetime.now(timezone.utc) - timedelta(days=2)
        TicketRepository.update_status(t2_id, "Resolved", resolved_at=resolved_time2)

        MessageRepository.create(
            message_id="msg_dash_01",
            ticket_id=t2_id,
            sender="customer",
            message="My dashboard disconnects every 10 minutes and forces me to sign back in.",
        )

        ResolutionRepository.create(
            resolution_id="res_dash_002",
            ticket_id=t2_id,
            root_cause="Inactive session timeout threshold was configured to default 600s (10 min) in organization policy",
            troubleshooting_steps="Inspected SSO token expiration logs, audited tenant session idle policies, and verified JWT expiry.",
            solution="Increased session timeout parameter to 28800s (8 hours) in tenant security settings.",
            outcome="Successfully resolved",
            resolution_time=18,
            customer_feedback="Session now remains active all day. Problem solved.",
        )

        # Retain into Hindsight persistent memory
        memory_manager.retain_experience(
            customer_id=cust2.customer_id,
            ticket_id=t2_id,
            issue="My dashboard disconnects every 10 minutes unexpectedly",
            category="Application / Session",
            root_cause="Inactive session timeout threshold was configured to default 600s (10 min) in organization policy",
            troubleshooting_steps="Inspected SSO token expiration logs, audited tenant session idle policies, and verified JWT expiry.",
            solution="Increased session timeout parameter to 28800s (8 hours) in tenant security settings.",
            outcome="Successfully resolved",
            environment="macOS Sonoma 14.3 + Safari 17",
            customer_feedback="Session now remains active all day. Problem solved.",
        )

    # --- Customer 3: Alex Rivera (Fresh customer for WITHOUT MEMORY demo) ---
    CustomerRepository.create(
        customer_id="cust_alex_rivera",
        name="Alex Rivera",
        email="alex.rivera@cloudtech-innovations.io",
        product="Developer API Gateway",
        plan="Developer",
        environment="Ubuntu 22.04 LTS + Firefox 124",
    )

    logger.info("Demo data seeding completed successfully.")
    return True
