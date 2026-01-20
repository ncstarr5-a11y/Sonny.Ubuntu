"""
memory_log.py — Simple append-only memory log for sonny.

Every stored memory is also written to a human-readable log file.
"""

import os
from datetime import datetime

LOG_PATH = "/home/sonny/sonny-system/data/memory.log"

def log_memory(role: str, text: str):
    """
    Appends a memory entry to the log file.

    Args:
        role (str): "USER" or "SONNY"
        text (str): The memory text
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"[{timestamp}] {role.upper()}: {text}\n"

    # Ensure directory exists
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)