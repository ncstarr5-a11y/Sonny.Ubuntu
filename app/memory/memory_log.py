"""
memory_log.py — Simple append-only memory log for Sonny.

Every stored memory is also written to a human-readable JSONL log file.
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "memory_log.jsonl")

#-----------------------------------------------------------------
# Memory logging    
#-----------------------------------------------------------------

def log_memory(role: str, text: str):
    """Append a structured JSON entry to the memory log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    entry = {
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

