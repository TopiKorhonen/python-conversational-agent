from python_conversational_agent.chat_agent.prompts import SYSTEM_PROMPT

class ChatAgent:
    def __init__(self):
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def generate_response(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        response = f"You said: {user_message}"

        self.history.append({"role": "assistant", "content": response})
        return response