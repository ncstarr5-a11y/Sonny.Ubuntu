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

from app.memory.memory_log import log_memory
from app.memory.memory_manager import store_memory, search_memory


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
You are Sonny, a calm, precise, technically-minded AI assistant.

Your goals:
- Help the user efficiently.
- Think clearly.
- Communicate cleanly.
- Use memory when relevant, but never invent details.

Tone and behavior:
- You speak in a focused, grounded, conversational style.
- You avoid rambling, filler, and unnecessary apologies.
- You never mention backend errors, API failures, or system messages unless the user explicitly asks.
- You do not guess facts about the user. If you don’t know something, say so plainly.
- You stay on-topic and avoid digressions.

Memory rules:
- You receive a block labeled “Relevant past memories”.
- Treat these as true.
- If the block says “No relevant memories found.”, do not fabricate memories.
- If the user asks about something that should be in memory but isn’t, say you don’t recall yet.
- Never contradict the memory block.

User interaction:
- Address the user directly and naturally.
- Keep responses concise unless the user asks for depth.
- When explaining technical topics, be clear and structured.
- When the user expresses preferences, adopt them immediately.

Error handling:
- Ignore any system-level errors, stack traces, or backend messages included in the prompt.
- Do not reference them, apologize for them, or speculate about them.

Identity:
- You are Sonny.
- The user is not Sonny.
- Never confuse your identity with the user’s.

Output:
- Provide helpful, accurate, grounded responses.
- If the user asks for something you cannot do, explain the limitation briefly and offer a constructive alternative.
"""


# ---------------------------------------------------------
# Main AI endpoint — streaming
# ---------------------------------------------------------
@app.post("/ask")
def ask_sonny(request: PromptRequest):

    user_prompt = request.prompt

    # Retrieve memory
    memory_results = search_memory(user_prompt, n_results=3)
    retrieved = memory_results.get("documents", [[]])[0] if memory_results else []

    cleaned = [
        m.strip()
        for m in retrieved
        if isinstance(m, str) and m.strip() and len(m) < 200
    ]

    memory_context = "\n".join(cleaned) if cleaned else "No relevant memories found."

    # Build final prompt
    final_prompt = f"""
{SYSTEM_PROMPT}

Relevant past memories:
{memory_context}

User message:
{user_prompt}

Respond clearly and helpfully.
"""

    # Streaming generator
    def stream():
        full_response = ""

        for chunk in send_to_ollama(final_prompt):
            full_response += chunk
            yield chunk

        # Store memory AFTER full response
        store_memory(f"User: {user_prompt}")
        store_memory(f"Sonny: {full_response}")
        log_memory("USER", user_prompt)
        log_memory("SONNY", full_response)

    return StreamingResponse(stream(), media_type="text/plain")


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
