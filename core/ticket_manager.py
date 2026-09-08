import json
import os
import random
from datetime import datetime, timezone

class TicketManager:
    
    def __init__(self, data_file="data/tickets.json"):
        self.data_file = data_file
        self.tickets = {}
        self._load_data()
    
    def _load_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "r", encoding="utf-8") as file:
                self.tickets = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tickets = {}
    
    def _save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(self.tickets, file, indent=4, ensure_ascii=False)
    
    def generate_ticket_id(self):
        return f"T-{random.randint(1000, 9999)}"
    
    def create_ticket(self, ticket_id, user_id, ticket_type, channel_id, title, reason):
        self.tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "title": title,
            "user_id": user_id,
            "type": ticket_type,
            "channel_id": channel_id,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": None,
            "status": "open",
            "claimed_by": None,
            "messages": []
        }
        self._save_data()
    
    def close_ticket(self, ticket_id):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = "closed"
            self.tickets[ticket_id]["closed_at"] = datetime.now(timezone.utc).isoformat()
            self._save_data()
    
    def claim_ticket(self, ticket_id, staff_id):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["claimed_by"] = staff_id
            self._save_data()
    
    def add_message(self, channel_id, author_name, author_id, content):
        for ticket_id, data in self.tickets.items():
            if data["channel_id"] == channel_id and data["status"] == "open":
                data["messages"].append({
                    "author": author_name,
                    "author_id": author_id,
                    "content": content,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                self._save_data()
                return True
        return False
    
    def get_statistics(self):
        total = len(self.tickets)
        open_count = sum(1 for ticket in self.tickets.values() if ticket["status"] == "open")
        closed_count = sum(1 for ticket in self.tickets.values() if ticket["status"] == "closed")
        return total, open_count, closed_count
    
    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id)

TicketManagerInstance = TicketManager()