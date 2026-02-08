'''This is the file custom memory that I control. No privacy bullshit boundries. 
This is the file that will store:
residents, reminders, events, preferences, routines and identity mappings, anything personal, anything important, anything Sonny needs to recall
This is the file that replaces the built‑in memory entirely — Sonny will only recall what’s in here, and nothing else.
This is the file that i can edit, structure, and manage however i like. It’s a blank slate for my creative genuis Tony stark shit. Its
This is the file that Sonny will read from and write to when storing and retrieving memories. It’s Sonny’s long‑term memory system. not the bellend version'''

import json
import os
from datetime import datetime, timedelta

BASE_DIR = "/home/sonny/sonny-system/data/memory"

FILES = {
    "residents": "residents.json",
    "reminders": "reminders.json",
    "calendar": "calendar_cache.json",
    "preferences": "preferences.json",
    "routines": "routines.json"
}


# -----------------------------
# INTERNAL HELPERS
# -----------------------------

def _ensure_file(path, default):
    """Create file with default content if missing."""
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)


def _load(path, default):
    """Load JSON safely, return default if corrupted."""
    _ensure_file(path, default)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default


def _save(path, data):
    """Write JSON safely."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _path(name):
    """Get full path for a memory file."""
    return os.path.join(BASE_DIR, FILES[name])


# -----------------------------
# RESIDENTS
# -----------------------------

def get_resident_name(resident_id):
    data = _load(_path("residents"), {})
    return data.get(resident_id, None)


def set_resident(resident_id, name):
    data = _load(_path("residents"), {})
    data[resident_id] = name
    _save(_path("residents"), data)


# -----------------------------
# REMINDERS
# -----------------------------

def add_reminder(title, event_time, remind_before_minutes=60):
    """
    event_time: ISO string "2026-02-08T14:00:00"
    """
    data = _load(_path("reminders"), {"reminders": []})

    event_dt = datetime.fromisoformat(event_time)
    remind_at = event_dt - timedelta(minutes=remind_before_minutes)

    reminder = {
        "id": f"rem_{int(datetime.now().timestamp())}",
        "title": title,
        "event_time": event_time,
        "remind_at": remind_at.isoformat(),
        "delivered": False
    }

    data["reminders"].append(reminder)
    _save(_path("reminders"), data)

    return reminder


def get_due_reminders():
    """Return reminders that should trigger now."""
    data = _load(_path("reminders"), {"reminders": []})
    now = datetime.now()

    due = []
    for r in data["reminders"]:
        remind_at = datetime.fromisoformat(r["remind_at"])
        if not r["delivered"] and remind_at <= now:
            due.append(r)

    return due


def mark_reminder_delivered(reminder_id):
    data = _load(_path("reminders"), {"reminders": []})
    for r in data["reminders"]:
        if r["id"] == reminder_id:
            r["delivered"] = True
    _save(_path("reminders"), data)


# -----------------------------
# CALENDAR CACHE
# -----------------------------

def update_calendar(events):
    """
    events: list of dicts
    Example event:
    {
        "id": "evt_001",
        "title": "Mia dance class",
        "time": "2026-02-08T16:00:00",
        "person": "resident_3"
    }
    """
    _save(_path("calendar"), {"events": events})


def get_events_for_resident(resident_id):
    data = _load(_path("calendar"), {"events": []})
    return [e for e in data["events"] if e.get("person") == resident_id]


# -----------------------------
# PREFERENCES
# -----------------------------

def set_preference(key, value):
    data = _load(_path("preferences"), {})
    data[key] = value
    _save(_path("preferences"), data)


def get_preference(key, default=None):
    data = _load(_path("preferences"), {})
    return data.get(key, default)