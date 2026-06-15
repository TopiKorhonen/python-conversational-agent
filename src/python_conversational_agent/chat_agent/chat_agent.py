from python_conversational_agent.chat_agent.agent_response import AgentResponse
from python_conversational_agent.chat_agent.prompts import SYSTEM_PROMPT
from ollama import chat

class ChatAgent:
    def __init__(self, model: str = "mistral"):
        self.model = model
    
    def generate_response(self, user_message: str) -> AgentResponse:
        try:
            response = chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            )
            text = response['message']['content']
        except Exception as e:
            # Fallback if Ollama is not running
            text = f"Error: Could not reach Ollama. Make sure it's running. ({str(e)})"
        
        # Determine emotion from the response
        emotion = self._detect_emotion(text, user_message)
        
        return AgentResponse(text, emotion)
    
    def _detect_emotion(self, response_text: str, user_message: str) -> str:
        """Detect emotion from the conversation context"""
        msg_lower = user_message.lower() + " " + response_text.lower()
        
        if any(w in msg_lower for w in ["happy", "great", "awesome", "excellent", "wonderful"]):
            return "happy"
        elif any(w in msg_lower for w in ["sad", "sorry", "unfortunately", "problem", "issue"]):
            return "concerned"
        elif "?" in user_message:
            return "thinking"
        else:
            return "neutral"