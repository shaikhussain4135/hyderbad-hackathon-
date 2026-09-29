"""Hindsight persistent memory manager for AI Customer Support Agent.

Integrates with the official hindsight-client SDK for retaining, recalling, and exploring
support experiences, with a resilient local memory fallback when the server is offline.
"""
import json
import socket
import uuid
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from utils.config import config
from utils.logging import logger

try:
    from hindsight_client import Hindsight
    HINDSIGHT_AVAILABLE = True
except ImportError:
    HINDSIGHT_AVAILABLE = False


class HindsightMemoryManager:
    """Manages AI agent persistent memory with official Hindsight SDK."""
    def __init__(self):
        try:
            local_dir = Path(__file__).resolve().parent.parent / "local_storage"
            local_dir.mkdir(exist_ok=True)
            self.fallback_file = local_dir / "hindsight_memories.json"
        except (OSError, PermissionError):
            local_dir = Path("/tmp") / "customer_agent_storage"
            local_dir.mkdir(exist_ok=True)
            self.fallback_file = local_dir / "hindsight_memories.json"

        if not self.fallback_file.exists():
            try:
                self.fallback_file.write_text("[]", encoding="utf-8")
            except Exception:
                pass

    def _is_server_reachable(self, url: str) -> bool:
        """Quick 250ms socket check to determine if host/port is accepting connections."""
        try:
            parsed = urlparse(url)
            host = parsed.hostname or "localhost"
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.25)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _get_client(self) -> Optional[Any]:
        """Instantiate official Hindsight client if available and configured."""
        if not HINDSIGHT_AVAILABLE:
            return None
        url = config.hindsight_url
        if not url or not self._is_server_reachable(url):
            return None
        try:
            return Hindsight(base_url=url, api_key=config.hindsight_api_key, timeout=2.0)
        except Exception as e:
            logger.warning(f"Could not initialize Hindsight client: {str(e)}")
            return None

    def test_connection(self) -> Tuple[bool, str]:
        """Test Hindsight connection safely without leaking secrets."""
        if not HINDSIGHT_AVAILABLE:
            return False, "hindsight-client Python package is not installed."
        url = config.hindsight_url
        if not url:
            return False, "HINDSIGHT_URL is not configured."

        if not self._is_server_reachable(url):
            return False, f"Hindsight server is not reachable at {url}. (Verify Hindsight service is running)"

        try:
            client = self._get_client()
            if not client:
                return False, f"Could not initialize Hindsight client for {url}."
            version_info = client.get_version()
            version_str = getattr(version_info, "version", "Connected")
            return True, f"Connected to Hindsight server (version: {version_str})"
        except Exception as e:
            return False, f"Hindsight connection error: {type(e).__name__}"

    def _get_bank_id(self, customer_id: Optional[str] = None) -> str:
        """Return canonical bank ID for memory isolation."""
        return "customer_support_kb"

    def retain_experience(
        self,
        customer_id: str,
        ticket_id: str,
        issue: str,
        category: str,
        root_cause: str,
        troubleshooting_steps: str,
        solution: str,
        outcome: str = "Resolved",
        environment: str = "Unknown",
        customer_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retain support experience in Hindsight memory.
        Stores structured facts, root causes, failed & successful approaches.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        memory_id = f"mem_{uuid.uuid4().hex[:10]}"

        # Structured textual memory content for semantic reasoning
        formatted_content = (
            f"CUSTOMER INTERACTION & RESOLUTION EXPERIENCE:\n"
            f"- Customer ID: {customer_id}\n"
            f"- Ticket ID: {ticket_id}\n"
            f"- Issue Description: {issue}\n"
            f"- Category: {category}\n"
            f"- Customer Environment: {environment}\n"
            f"- Identified Root Cause: {root_cause}\n"
            f"- Troubleshooting Steps Applied: {troubleshooting_steps}\n"
            f"- Successful Solution: {solution}\n"
            f"- Outcome: {outcome}\n"
            f"- Customer Feedback: {customer_feedback or 'None'}\n"
            f"- Recorded At: {timestamp}"
        )

        metadata = {
            "customer_id": customer_id,
            "ticket_id": ticket_id,
            "category": category,
            "root_cause": root_cause,
            "solution": solution,
            "outcome": outcome,
            "environment": environment,
            "memory_id": memory_id,
            "timestamp": timestamp,
        }

        tags = [f"cust:{customer_id}", f"cat:{category.lower()}", "resolution", outcome.lower()]

        # Try live Hindsight server
        saved_live = False
        client = self._get_client()
        if client:
            try:
                bank_id = self._get_bank_id(customer_id)
                client.retain(
                    bank_id=bank_id,
                    content=formatted_content,
                    context=f"Support ticket {ticket_id} for customer {customer_id}",
                    metadata=metadata,
                    tags=tags,
                )
                saved_live = True
                logger.info(f"Retained experience {memory_id} in Hindsight server bank '{bank_id}'")
            except Exception as e:
                logger.warning(f"Could not retain to live Hindsight ({str(e)}). Storing in persistent backup bank.")

        # Always persist in local bank for offline resilience & Explorer
        record = {
            "memory_id": memory_id,
            "bank_id": self._get_bank_id(customer_id),
            "customer_id": customer_id,
            "ticket_id": ticket_id,
            "issue": issue,
            "category": category,
            "environment": environment,
            "root_cause": root_cause,
            "troubleshooting_steps": troubleshooting_steps,
            "solution": solution,
            "outcome": outcome,
            "customer_feedback": customer_feedback,
            "formatted_text": formatted_content,
            "metadata": metadata,
            "tags": tags,
            "timestamp": timestamp,
            "stored_in_live_server": saved_live,
        }
        self._append_local_memory(record)
        return record

    def recall_experiences(
        self,
        customer_id: str,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories from Hindsight.
        Falls back smoothly to local memory bank if server is unreachable.
        """
        recalled: List[Dict[str, Any]] = []
        client = self._get_client()

        if client:
            try:
                bank_id = self._get_bank_id(customer_id)
                response = client.recall(
                    bank_id=bank_id,
                    query=query,
                    max_tokens=2048,
                    tags=[f"cust:{customer_id}"] if customer_id else None
                )
                if response and hasattr(response, "results") and response.results:
                    for res in response.results:
                        meta = getattr(res, "metadata", {}) or {}
                        recalled.append({
                            "memory_id": getattr(res, "id", None) or meta.get("memory_id", "mem_hindsight"),
                            "text": getattr(res, "text", ""),
                            "customer_id": meta.get("customer_id", customer_id),
                            "ticket_id": meta.get("ticket_id", "N/A"),
                            "issue": meta.get("issue", ""),
                            "root_cause": meta.get("root_cause", ""),
                            "solution": meta.get("solution", ""),
                            "outcome": meta.get("outcome", "Resolved"),
                            "environment": meta.get("environment", ""),
                            "source": "Hindsight Server",
                            "score": 0.95,
                        })
                    if recalled:
                        return recalled[:top_k]
            except Exception as e:
                logger.warning(f"Hindsight live recall failed ({str(e)}). Querying local memory bank.")

        # Fallback to local memory bank
        return self._search_local_memory(customer_id=customer_id, query=query, category=category, top_k=top_k)

    def list_all_memories(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all stored memories for Memory Explorer."""
        all_mems = self._read_local_memories()
        if customer_id:
            all_mems = [m for m in all_mems if m.get("customer_id") == customer_id]
        return sorted(all_mems, key=lambda x: x.get("timestamp", ""), reverse=True)

    def _read_local_memories(self) -> List[Dict[str, Any]]:
        try:
            if self.fallback_file.exists():
                data = json.loads(self.fallback_file.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error reading local memory store: {str(e)}")
        return []

    def _append_local_memory(self, record: Dict[str, Any]):
        memories = self._read_local_memories()
        # Avoid duplicate memory_id
        memories = [m for m in memories if m.get("memory_id") != record.get("memory_id")]
        memories.append(record)
        self.fallback_file.write_text(json.dumps(memories, indent=2), encoding="utf-8")

    def _search_local_memory(
        self,
        customer_id: str,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Precision keyword and semantic token matching over local memory bank."""
        all_memories = self._read_local_memories()
        
        # Filter stopwords
        stopwords = {
            "the", "and", "for", "with", "this", "that", "from", "when", "what",
            "after", "fails", "failure", "error", "issue", "problem", "help",
            "again", "every", "time", "using", "does", "cannot", "report", "reports"
        }
        
        raw_words = query.lower().replace(".", " ").replace(",", " ").replace("-", " ").replace("/", " ").split()
        query_words = {w for w in raw_words if len(w) > 2 and w not in stopwords}

        scored_memories = []
        for mem in all_memories:
            mem_cust = mem.get("customer_id", "")
            
            # If customer_id is specified, strictly isolate to this customer's interactions
            if customer_id and mem_cust != customer_id:
                continue

            searchable_text = (
                f"{mem.get('issue', '')} {mem.get('category', '')} {mem.get('root_cause', '')} "
                f"{mem.get('solution', '')} {mem.get('environment', '')}"
            ).lower()

            matched_words = [w for w in query_words if w in searchable_text]
            
            if len(matched_words) >= 1:
                score = len(matched_words) * 2.5
                scored_memories.append((score, mem))

        # Sort by relevance score descending
        scored_memories.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, mem in scored_memories[:top_k]:
            results.append({
                "memory_id": mem.get("memory_id"),
                "text": mem.get("formatted_text"),
                "customer_id": mem.get("customer_id"),
                "ticket_id": mem.get("ticket_id"),
                "issue": mem.get("issue"),
                "root_cause": mem.get("root_cause"),
                "solution": mem.get("solution"),
                "outcome": mem.get("outcome"),
                "environment": mem.get("environment"),
                "source": "Hindsight Memory Bank (Local Persistent)",
                "score": round(min(score / 10.0, 0.99), 2),
            })
        return results


memory_manager = HindsightMemoryManager()
