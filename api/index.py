"""Vercel Serverless Entrypoint for Customer Support Memory Agent."""
import json
from http.server import BaseHTTPRequestHandler
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.database import get_connection_info, test_db_connection
from memory.hindsight_manager import memory_manager
from llm.llm_client import llm_client
from services.resolution_service import ResolutionService
from agents.support_agent import support_agent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        metrics = ResolutionService.get_dashboard_metrics()
        db_name, is_neon = get_connection_info()
        hs_ok, hs_msg = memory_manager.test_connection()
        llm_ok, llm_msg = llm_client.test_connection()

        payload = {
            "project": "Customer Support Memory Agent",
            "version": "1.0.0",
            "status": "online",
            "services": {
                "database": {"name": db_name, "live_neon": is_neon},
                "hindsight": {"connected": hs_ok, "status": hs_msg},
                "llm": {"connected": llm_ok, "provider": llm_msg},
            },
            "metrics": metrics,
            "instructions": {
                "ui_access": "Run 'python -m streamlit run app.py' locally or host via Streamlit Community Cloud",
                "login_accounts": ["admin/admin123", "agent/support123", "judge/hackathon2026"],
            }
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(body) if body else {}
            customer_id = data.get("customer_id", "cust_john_smith")
            issue = data.get("issue", "My PDF upload is failing again.")
            result = support_agent.process_ticket(customer_id=customer_id, issue_description=issue)
            response = {"success": True, "result": result}
            self.send_response(200)
        except Exception as e:
            response = {"success": False, "error": str(e)}
            self.send_response(500)

        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))
