import json
import os
import random
from datetime import datetime, timezone

class TicketManager:
    def __init__(self, data_file="data/tickets.json"):
        self.data_file = data_file
        self.tickets = {}
        self._load()

    def _load(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.tickets = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tickets = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tickets, f, indent=4, ensure_ascii=False)

    def generate_id(self):
        return f"T-{random.randint(1000, 9999)}"

    def create(self, tid, user_id, ttype, channel_id, title, reason):
        self.tickets[tid] = {
            "ticket_id": tid,
            "title": title,
            "user_id": user_id,
            "type": ttype,
            "channel_id": channel_id,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": None,
            "status": "open",
            "claimed_by": None,
            "messages": []
        }
        self._save()

    def close(self, tid):
        if tid in self.tickets:
            self.tickets[tid]["status"] = "closed"
            self.tickets[tid]["closed_at"] = datetime.now(timezone.utc).isoformat()
            self._save()

    def claim(self, tid, staff_id):
        if tid in self.tickets:
            self.tickets[tid]["claimed_by"] = staff_id
            self._save()

    def add_message(self, channel_id, author, author_id, content):
        for tid, data in self.tickets.items():
            if data["channel_id"] == channel_id and data["status"] == "open":
                data["messages"].append({
                    "author": author,
                    "author_id": author_id,
                    "content": content,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                self._save()
                return

    def get_stats(self):
        total = len(self.tickets)
        open_t = sum(1 for t in self.tickets.values() if t["status"] == "open")
        closed_t = sum(1 for t in self.tickets.values() if t["status"] == "closed")
        return total, open_t, closed_t

# ✅ اینجا یک نمونه (instance) از کلاس می‌سازیم
ticket_manager = TicketManager()