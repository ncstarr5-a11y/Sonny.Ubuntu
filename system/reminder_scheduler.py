import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custom_memory

def notify(reminder):
    print(f"[REMINDER] {reminder['title']} (Event at {reminder['event_time']})")

def run_scheduler():
    print("Reminder scheduler running...")

    while True:
        due = custom_memory.get_due_reminders()

        if due:
            for r in due:
                notify(r)
                custom_memory.mark_reminder_delivered(r["id"])

        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()