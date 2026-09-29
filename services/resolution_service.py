"""Resolution business logic and analytics service."""
from typing import List, Optional, Dict, Any
from database.models import Resolution
from database.repositories import ResolutionRepository, TicketRepository, CustomerRepository
from memory.hindsight_manager import memory_manager


class ResolutionService:
    @staticmethod
    def get_by_ticket(ticket_id: str) -> Optional[Resolution]:
        return ResolutionRepository.get_by_ticket(ticket_id)

    @staticmethod
    def list_all() -> List[Resolution]:
        return ResolutionRepository.list_all()

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Compute real calculated metrics across customers, tickets, and resolutions."""
        customers = CustomerRepository.list_all()
        tickets = TicketRepository.list_all()
        resolutions = ResolutionRepository.list_all()
        memories = memory_manager.list_all_memories()

        total_customers = len(customers)
        total_tickets = len(tickets)
        open_tickets = sum(1 for t in tickets if t.status == "Open")
        resolved_tickets = sum(1 for t in tickets if t.status == "Resolved")

        # Memory assisted resolutions: resolutions that have a matching memory entry
        resolved_ticket_ids = {r.ticket_id for r in resolutions}
        memory_assisted_count = sum(1 for m in memories if m.get("ticket_id") in resolved_ticket_ids or m.get("ticket_id"))

        avg_resolution_time = 0.0
        if resolutions:
            avg_resolution_time = round(sum(r.resolution_time for r in resolutions) / len(resolutions), 1)

        resolution_rate = round((resolved_tickets / total_tickets * 100), 1) if total_tickets > 0 else 0.0

        return {
            "total_customers": total_customers,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_tickets": resolved_tickets,
            "resolution_rate": resolution_rate,
            "memory_assisted_resolutions": memory_assisted_count,
            "average_resolution_time_mins": avg_resolution_time,
            "total_memories_stored": len(memories),
            "recent_tickets": [t.to_dict() for t in tickets[:5]],
            "recent_resolutions": [r.to_dict() for r in resolutions[:5]],
        }
