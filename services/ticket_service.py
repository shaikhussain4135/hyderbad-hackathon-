"""Ticket business logic service."""
import uuid
from typing import List, Optional
from database.models import Ticket
from database.repositories import TicketRepository, MessageRepository


class TicketService:
    @staticmethod
    def create_ticket(
        customer_id: str,
        issue: str,
        category: str = "General",
        severity: str = "Medium",
    ) -> Ticket:
        ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        ticket = TicketRepository.create(
            ticket_id=ticket_id,
            customer_id=customer_id,
            issue=issue,
            category=category,
            severity=severity,
            status="Open",
        )
        # Record initial customer message
        MessageRepository.create(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            ticket_id=ticket_id,
            sender="customer",
            message=issue,
        )
        return ticket

    @staticmethod
    def get_ticket(ticket_id: str) -> Optional[Ticket]:
        return TicketRepository.get_by_id(ticket_id)

    @staticmethod
    def list_tickets(customer_id: Optional[str] = None, status: Optional[str] = None) -> List[Ticket]:
        return TicketRepository.list_all(customer_id=customer_id, status=status)
