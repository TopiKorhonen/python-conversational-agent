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
        msg_lower = user_message.lower()
        resp_lower = response_text.lower()

        # Question asked → mascot thinks while responding
        if "?" in user_message:
            return "thinking"
        # Positive/happy language
        if any(w in msg_lower + " " + resp_lower 
               for w in ["happy", "great", "awesome", "excellent", "wonderful", 
                         "amazing", "fantastic", "love", "perfect"]):
            return "happy"
        # Problem/concern language
        if any(w in resp_lower 
               for w in ["sorry", "unfortunately", "problem", "issue", "error", "can't"]):
            return "concerned"

        return "neutral"