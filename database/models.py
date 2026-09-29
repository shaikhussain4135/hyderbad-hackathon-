"""SQLAlchemy ORM models for Neon PostgreSQL structured relational data."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(128), nullable=False)
    plan: Mapped[str] = mapped_column(String(64), nullable=False, default="Standard")
    environment: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "product": self.product,
            "plan": self.plan,
            "environment": self.environment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(64), ForeignKey("customers.customer_id"), nullable=False, index=True)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False, default="General")
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="Medium")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Open", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="tickets")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="ticket", cascade="all, delete-orphan")
    resolutions: Mapped[List["Resolution"]] = relationship("Resolution", back_populates="ticket", cascade="all, delete-orphan")

    def to_dict(self):
        cust_name = "Unknown"
        if "customer" in self.__dict__ and self.customer:
            cust_name = self.customer.name
        return {
            "ticket_id": self.ticket_id,
            "customer_id": self.customer_id,
            "customer_name": cust_name,
            "issue": self.issue,
            "category": self.category,
            "severity": self.severity,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(64), nullable=False)  # 'customer' | 'agent' | 'system'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="messages")

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "ticket_id": self.ticket_id,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class Resolution(Base):
    __tablename__ = "resolutions"

    resolution_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    troubleshooting_steps: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False, default="Resolved")
    resolution_time: Mapped[int] = mapped_column(Integer, nullable=False, default=15)  # minutes
    customer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="resolutions")

    def to_dict(self):
        return {
            "resolution_id": self.resolution_id,
            "ticket_id": self.ticket_id,
            "root_cause": self.root_cause,
            "troubleshooting_steps": self.troubleshooting_steps,
            "solution": self.solution,
            "outcome": self.outcome,
            "resolution_time": self.resolution_time,
            "customer_feedback": self.customer_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
