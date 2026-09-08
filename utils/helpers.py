import os
import json

def save_ticket_log(data, filename):
    os.makedirs("data/logs", exist_ok=True)
    path = f"data/logs/{filename}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return path