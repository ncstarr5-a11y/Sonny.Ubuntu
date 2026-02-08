import system.custom_memory

ACTIONS = {
    "memory.add_reminder": lambda p: system.custom_memory.add_reminder(
        title=p["title"],
        event_time=p["event_time"]
    ),
}

def execute_action(action):
    name = action["name"]
    params = action["params"]

    if name not in ACTIONS:
        return f"Unknown action: {name}"

    try:
        result = ACTIONS[name](params)
        return f"Action {name} executed."
    except Exception as e:
        return f"Error executing {name}: {e}"