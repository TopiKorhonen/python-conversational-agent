import json
import os
import urllib.request
from python_conversational_agent.chat_agent.prompts import SYSTEM_PROMPT

class ChatAgent:
    def __init__(self, model=None):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral:latest")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate_response(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": False,
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.load(response)
            reply = result["message"]["content"].strip()
        except Exception:
            reply = "Sorry, the local model is not available. Check that Ollama is running."

        self.history.append({"role": "assistant", "content": reply})
        return reply