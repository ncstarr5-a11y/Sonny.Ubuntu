import sys
import os
import time
import system.custom_memory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def notify(reminder):
    print(f"[REMINDER] {reminder['title']} (Event at {reminder['event_time']})")

def run_scheduler():
    print("Reminder scheduler running...")

    while True:
        due = system.custom_memory.get_due_reminders()

        if due:
            for r in due:
                notify(r)
                system.custom_memory.mark_reminder_delivered(r["id"])

        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()