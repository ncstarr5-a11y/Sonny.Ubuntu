# Sonny1.0 — AI Assistant Backend

This folder contains the backend code for **Sonny1.0**, your personal AI assistant.
The backend is built using **FastAPI**, a modern Python web framework.

---

## 📁 Project Structure (Simplified)

sonny-system/ │ ├── app/ │   ├── main.py          # Entrypoint for the API │   ├── brain/           # AI logic (future) │   ├── memory/          # Long-term memory (future) │   ├── actions/         # Things Sonny can do (future) │   ├── api/             # API endpoints (future) │   └── utils/           # Helper functions (future) │ ├── data/                # Memory, logs, configs └── venv/                # Python virtual environment

---

# 🚀 Running Sonny1.0

## 1. Activate the virtual environment

cd /home/sonny/sonny-system source venv/bin/activate


## 2. Start the FastAPI server

 uvicorn app.main:app --reload


## 3. Test the API

Open your browser:
http://127.0.0.1:8000

Or use curl:

curl -X POST http://localhost:8000/ask -d '{"prompt":"Hello Sonny"}' -H "Content-Type: application/json"


---

# 🧠 How It Works

 1. You send a prompt to `/ask`
Example:

```json
{
  "prompt": "What is the weather like?"
}

2. The backend forwards the prompt to Ollama
Ollama runs your local AI model (e.g., llama3.1).

3. Ollama generates a response
The backend collects the streamed output.

4. The backend returns the response to you
Example:
{
  "prompt": "Hello Sonny",
  "response": "Greetings, young Padawan..."
}

Requirements
• 	Python 3.10+
• 	FastAPI
• 	Uvicorn
• 	Requests
• 	Ollama installed and running

Goal of Sonny1.0
This version is intentionally simple:
• 	One endpoint
• 	One model
• 	One brain function
It gives you a clean foundation to grow Sonny into a full AI ecosystem.

#################################################

## 🧠 Memory System (ChromaDB)

Sonny1.0 uses **ChromaDB** as its long-term memory engine.

### How it works

1. Text is converted into an embedding vector using Ollama.
2. The vector is stored in ChromaDB along with the original text.
3. When sonny needs to recall something, it searches for similar embeddings.

### Key files

- `chroma_client.py` — connects to ChromaDB
- `embeddings.py` — generates embeddings using Ollama
- `memory_manager.py` — stores and retrieves memories

### Example usage

```python
from app.memory.memory_manager import store_memory, search_memory

store_memory("Chris likes modular AI systems.")
results = search_memory("What does Chris like?")
print(results)
