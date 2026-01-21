"""
main.py — Entrypoint for sonny1.0

This file starts the FastAPI server that powers your AI assistant.
It exposes HTTP endpoints that your UI, scripts, or other devices
can call to interact with sonny.

As sonny grows, this file will remain the "front door" to the system.
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.memory.memory_log import log_memory
from app.memory.memory_manager import store_memory, search_memory
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
    title="sonny1.0 API",
    description="Backend API for your personal AI assistant.",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# Request model for sending prompts to sonny
# ---------------------------------------------------------
class PromptRequest(BaseModel):
    """
    Defines the structure of the JSON body expected when
    sending a prompt to sonny.

    Example:
    {
        "prompt": "Hello sonny, how are you?"
    }
    """
    prompt: str

# ---------------------------------------------------------
# Helper function: Send prompt to Ollama
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
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk

    except Exception as e:
        yield f"[ERROR contacting Ollama] {str(e)}"




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
    return {"status": "sonny1.0 online", "message": "System operational."}


# ---------------------------------------------------------
# Main AI endpoint — send a prompt to sonny
# -------------------------------------------------------
@app.post("/ask")
def ask_sonny(request: PromptRequest):

    user_prompt = request.prompt

    # memory retrieval stays the same
    memory_results = search_memory(user_prompt, n_results=3)
    retrieved_memories = memory_results.get("documents", [[]])[0] if memory_results else []

    cleaned_memories = [m.strip() for m in retrieved_memories if isinstance(m, str) and m.strip()]
    memory_context = "\n".join(cleaned_memories)

    final_prompt = f"""
You are sonny, a helpful AI assistant.

Relevant past memories:
{memory_context}

User message:
{user_prompt}

Respond clearly and helpfully.
"""

    # streaming generator
    def stream():
        full_response = ""
        for chunk in send_to_ollama(final_prompt):
            full_response += chunk
            yield chunk

        # store memory after full response is complete
        store_memory(f"User: {user_prompt}")
        store_memory(f"sonny: {full_response}")
        log_memory("USER", user_prompt)
        log_memory("SONNY", full_response)

    return StreamingResponse(stream(), media_type="text/plain")




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
    Serves the sonny web interface.
    """
    return FileResponse("app/ui/index.html")
#-------------------------------------------------------------------
# Store the new memory
#-------------------------------------------------------------------



