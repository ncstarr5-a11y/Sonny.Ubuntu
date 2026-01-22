"""
memory_log.py — Simple append-only memory log for sonny.

Every stored memory is also written to a human-readable log file.
"""

import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "memory_log.jsonl")


#  ---------------------------------------------------------
# Log a memory entry to the log file
# ---------------------------------------------------------

def log_memory(role: str, text: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(str(entry) + "\n")
