class ChatAgent:
    def __init__(self):
        self.history = []
    
    def generate_response(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        # Placeholder test response
        response = f"You said: {user_message}"

        self.history.append({"role": "assistant", "content": response})
        return response