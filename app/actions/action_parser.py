import re
import json

ACTION_PATTERN = re.compile(
    r"<action name=\"([^\"]+)\">(.*?)</action>",
    re.DOTALL
)

def extract_actions(text: str):
    actions = []
    for name, body in ACTION_PATTERN.findall(text):
        try:
            params = json.loads(body.strip())
        except json.JSONDecodeError:
            continue
        actions.append({"name": name, "params": params})
    return actions