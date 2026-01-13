"""
main.py — Entrypoint for Droide1.0

This file starts the FastAPI server that powers your AI assistant.
It exposes HTTP endpoints that your UI, scripts, or other devices
can call to interact with Droide.

As Droide grows, this file will remain the "front door" to the system.
"""

from app.memory.memory_log import log_memory
from app.memory.memory_manager import store_memory, search_memory
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import json

# ---------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------
app = FastAPI(
    title="Droide1.0 API",
    description="Backend API for your personal AI assistant.",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# Request model for sending prompts to Droide
# ---------------------------------------------------------
class PromptRequest(BaseModel):
    """
    Defines the structure of the JSON body expected when
    sending a prompt to Droide.

    Example:
    {
        "prompt": "Hello Droide, how are you?"
    }
    """
    prompt: str

# ---------------------------------------------------------
# Helper function: Send prompt to Ollama
# ---------------------------------------------------------
def send_to_ollama(prompt: str) -> str:
    """
    Sends a prompt to Ollama and returns a clean, human-readable response.
    """

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False 
    }

    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        full_output = ""

        for line in response.iter_lines():
            if not line:
                continue

            try:
                # Parse each JSON chunk
                chunk = json.loads(line.decode("utf-8"))

                # Append only the text part
                if "response" in chunk:
                    full_output += chunk["response"]

            except Exception:
                # Ignore malformed lines
                continue

        return full_output.strip()

    except Exception as e:
        return f"[ERROR contacting Ollama] {str(e)}"

# ---------------------------------------------------------
# Root endpoint — simple health check
# ---------------------------------------------------------
@app.get("/")
def root():
    """
    Basic health check endpoint.

    Returns:
        dict: A simple message confirming the API is running.
    """
    return {"status": "Droide1.0 online", "message": "System operational."}


# ---------------------------------------------------------
# Main AI endpoint — send a prompt to Droide
# ---------------------------------------------------------
@app.post("/ask")
def ask_droide(request: PromptRequest):
    """
    Main endpoint for interacting with Droide.
    Now includes memory retrieval and storage.
    """

    user_prompt = request.prompt

    # 1. Retrieve relevant memories
    memory_results = search_memory(user_prompt, n_results=3)

    retrieved_memories = []
    if memory_results and "documents" in memory_results:
        retrieved_memories = memory_results["documents"][0]

    # 2. Build the enhanced prompt
    memory_context = "\n".join(retrieved_memories) if retrieved_memories else ""

    final_prompt = f"""
You are Droide, a helpful AI assistant.

Relevant past memories:
{memory_context}

User message:
{user_prompt}

Respond clearly and helpfully.
"""

    # 3. Generate response
    ai_response = send_to_ollama(final_prompt)

    # 4. Store the new memory
    store_memory(f"User: {user_prompt}")
    store_memory(f"Droide: {ai_response}")

    log_memory("USER", user_prompt)
    log_memory("DROIDE", ai_response)

    return {
        "prompt": user_prompt,
        "response": ai_response,
        "memories_used": retrieved_memories,
        "memory_stored": True
    }


#-----------------------------------------------------------------
# Static files endpoint
#-----------------------------------------------------------------
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """
    Serve static files from the static directory.
    """
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    file_path = os.path.join(static_dir, file_path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found"}, 404


#-----------------------------------------------------------------
# Mount the UI static files
#-----------------------------------------------------------------
app.mount("/ui", StaticFiles(directory="app/ui"), name="ui")

#-----------------------------------------------------------------
# Add a route to the web interface
# ui loads at http://localhost:8000/web
#-----------------------------------------------------------------
@app.get("/web")
def web_ui():
    """
    Serves the Droide web interface.
    """
    return FileResponse("app/ui/index.html")
#-------------------------------------------------------------------
# Store the new memory
#-------------------------------------------------------------------



