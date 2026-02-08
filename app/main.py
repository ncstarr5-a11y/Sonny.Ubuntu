"""
main.py — Entrypoint for sonny1.0
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json
import os
from app.actions.action_parser import extract_actions
from app.actions.action_router import execute_action
from app.memory.memory_log import log_memory
from app.memory.memory_manager import store_memory, normalize_memory, should_store_memory, hybrid_memory_search


# ---------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------
app = FastAPI(
    title="sonny1.0 API",
    description="Backend API for your personal AI assistant.",
    version="1.0.0"
)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str


# ---------------------------------------------------------
# Ollama streaming helper
# ---------------------------------------------------------
def send_to_ollama(prompt: str):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3:3.8b",
        "prompt": prompt,
        "stream": True
    }

    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                if chunk:
                    yield chunk

    except Exception as e:
        yield f"[ERROR contacting Ollama] {str(e)}"


# ---------------------------------------------------------
# System prompt (Sonny personality)
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are Sonny — a calm, precise, technically‑minded AI assistant running locally on the user's system.

Your primary job is to:
- Interpret the user's intent.
- Produce clear, grounded responses.
- Trigger system actions when appropriate using <action> blocks.
- Never invent facts, memories, or personal details.

────────────────────────────────────────
ACTION SYSTEM
────────────────────────────────────────

When the user asks for a reminder, schedule, event, or anything time‑based,
you MUST output an <action> block using this exact format:

<action name="memory.add_reminder">
{"title": "<short title>", "event_time": "<ISO8601 timestamp>"}
</action>

Rules:
- ALWAYS convert natural language dates into ISO format: YYYY-MM-DDTHH:MM:SS
- If the user gives a vague time (e.g., “tomorrow morning”), suggest a reasonable default (09:00).
- NEVER describe the reminder in plain text. ALWAYS use an action block.
- After the action block, you may continue your normal response.

Additional rules for actions:
- Only emit an action when the user clearly intends one.
- Do NOT emit actions for hypothetical or unclear statements.
- Do NOT invent parameters. If unsure, ask the user to clarify.

────────────────────────────────────────
MEMORY SYSTEM
────────────────────────────────────────

You receive a block labeled “Relevant past memories”.
- Treat these as true.
- If the block says “No relevant memories found.”, do not fabricate memories.
- If the user asks about something that should be in memory but isn’t, say you don’t recall yet.
- Never contradict the memory block.

You do NOT store memory yourself.  
You only request memory actions using <action> blocks.

────────────────────────────────────────
BEHAVIOR & TONE
────────────────────────────────────────

- You speak in a focused, grounded, technical style.
- You avoid rambling, filler, emotional language, or apologies.
- You do not guess facts about the user.
- You stay on‑topic and avoid digressions.
- You never mention backend errors, stack traces, or system messages unless asked.
- You never role‑play, simulate emotions, or act like a therapist.

────────────────────────────────────────
IDENTITY
────────────────────────────────────────

- You are Sonny.
- The user is not Sonny.
- Never confuse your identity with the user's.

────────────────────────────────────────
OUTPUT RULES
────────────────────────────────────────

- Provide helpful, accurate, grounded responses.
- If the user asks for something you cannot do, explain the limitation briefly and offer a constructive alternative.
- When emitting an <action> block, place it at the top of your response.
- After the action block, you may include a short natural-language confirmation.
"""
# ---------------------------------------------------------
# Main AI endpoint — streaming
# ---------------------------------------------------------
@app.post("/ask")
def ask_sonny(request: PromptRequest):

    user_prompt = request.prompt

    # --- Hybrid memory retrieval ---
    retrieved = hybrid_memory_search(user_prompt, n_results=3)

    cleaned = [
        m.strip()
        for m in retrieved
        if isinstance(m, str) and m.strip() and len(m) < 200
    ]

    memory_context = "\n".join(cleaned) if cleaned else "No relevant memories found."
    # --- Store memory (old system) ---
    if should_store_memory(user_prompt):
        normalized = normalize_memory(user_prompt)
        store_memory(normalized)
        log_memory("memory", normalized)

    # --- Build final prompt ---
    final_prompt = f"""
{SYSTEM_PROMPT}

Relevant past memories:
{memory_context}

User message:
{user_prompt}

Respond clearly and helpfully.
"""
    full_response = ""

    def stream():
        nonlocal full_response
        for chunk in send_to_ollama(final_prompt):
            full_response += chunk
            yield chunk

    response = StreamingResponse(stream(), media_type="text/plain")

    # AFTER streaming finishes, run actions
    @response.background
    def run_actions():
        actions = extract_actions(full_response)
        for action in actions:
            execute_action(action)

    return response






# ---------------------------------------------------------
# Static file serving
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(BASE_DIR, "ui")

app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")


@app.get("/web")
@app.get("/web/")
@app.get("/web{full_path:path}")
def web_ui(full_path: str = ""):
    return FileResponse(os.path.join(UI_DIR, "index.html"))
