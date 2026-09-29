"""Repository layer for structured database operations."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update, desc
from sqlalchemy.orm import joinedload
from database.database import get_db_session
from database.models import Customer, Ticket, Message, Resolution


class CustomerRepository:
    @staticmethod
    def create(customer_id: str, name: str, email: str, product: str, plan: str, environment: str) -> Customer:
        with get_db_session() as session:
            existing = session.scalar(select(Customer).where(Customer.customer_id == customer_id))
            if existing:
                existing.name = name
                existing.email = email
                existing.product = product
                existing.plan = plan
                existing.environment = environment
                session.commit()
                session.refresh(existing)
                return existing
            customer = Customer(
                customer_id=customer_id,
                name=name,
                email=email,
                product=product,
                plan=plan,
                environment=environment,
                created_at=datetime.now(timezone.utc),
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer

    @staticmethod
    def get_by_id(customer_id: str) -> Optional[Customer]:
        with get_db_session() as session:
            return session.scalar(select(Customer).where(Customer.customer_id == customer_id))

    @staticmethod
    def get_by_email(email: str) -> Optional[Customer]:
        with get_db_session() as session:
            return session.scalar(select(Customer).where(Customer.email == email))

    @staticmethod
    def list_all() -> List[Customer]:
        with get_db_session() as session:
            return list(session.scalars(select(Customer).order_by(Customer.name)).all())


class TicketRepository:
    @staticmethod
    def create(ticket_id: str, customer_id: str, issue: str, category: str = "General", severity: str = "Medium", status: str = "Open") -> Ticket:
        with get_db_session() as session:
            ticket = Ticket(
                ticket_id=ticket_id,
                customer_id=customer_id,
                issue=issue,
                category=category,
                severity=severity,
                status=status,
                created_at=datetime.now(timezone.utc),
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            return ticket

    @staticmethod
    def get_by_id(ticket_id: str) -> Optional[Ticket]:
        with get_db_session() as session:
            return session.scalar(
                select(Ticket)
                .options(joinedload(Ticket.customer))
                .where(Ticket.ticket_id == ticket_id)
            )

    @staticmethod
    def list_all(customer_id: Optional[str] = None, status: Optional[str] = None) -> List[Ticket]:
        with get_db_session() as session:
            query = select(Ticket).options(joinedload(Ticket.customer)).order_by(desc(Ticket.created_at))
            if customer_id:
                query = query.where(Ticket.customer_id == customer_id)
            if status:
                query = query.where(Ticket.status == status)
            return list(session.scalars(query).all())

    @staticmethod
    def update_status(ticket_id: str, status: str, resolved_at: Optional[datetime] = None) -> bool:
        with get_db_session() as session:
            ticket = session.scalar(select(Ticket).where(Ticket.ticket_id == ticket_id))
            if not ticket:
                return False
            ticket.status = status
            if resolved_at:
                ticket.resolved_at = resolved_at
            session.commit()
            return True


class MessageRepository:
    @staticmethod
    def create(message_id: str, ticket_id: str, sender: str, message: str) -> Message:
        with get_db_session() as session:
            msg = Message(
                message_id=message_id,
                ticket_id=ticket_id,
                sender=sender,
                message=message,
                timestamp=datetime.now(timezone.utc),
            )
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg

    @staticmethod
    def get_by_ticket(ticket_id: str) -> List[Message]:
        with get_db_session() as session:
            return list(
                session.scalars(
                    select(Message).where(Message.ticket_id == ticket_id).order_by(Message.timestamp)
                ).all()
            )


class ResolutionRepository:
    @staticmethod
    def create(
        resolution_id: str,
        ticket_id: str,
        root_cause: str,
        troubleshooting_steps: str,
        solution: str,
        outcome: str = "Resolved",
        resolution_time: int = 15,
        customer_feedback: Optional[str] = None,
    ) -> Resolution:
        with get_db_session() as session:
            res = Resolution(
                resolution_id=resolution_id,
                ticket_id=ticket_id,
                root_cause=root_cause,
                troubleshooting_steps=troubleshooting_steps,
                solution=solution,
                outcome=outcome,
                resolution_time=resolution_time,
                customer_feedback=customer_feedback,
                created_at=datetime.now(timezone.utc),
            )
            session.add(res)
            session.commit()
            session.refresh(res)
            return res

    @staticmethod
    def get_by_ticket(ticket_id: str) -> Optional[Resolution]:
        with get_db_session() as session:
            return session.scalar(select(Resolution).where(Resolution.ticket_id == ticket_id))

    @staticmethod
    def list_all() -> List[Resolution]:
        with get_db_session() as session:
            return list(session.scalars(select(Resolution).order_by(desc(Resolution.created_at))).all())
