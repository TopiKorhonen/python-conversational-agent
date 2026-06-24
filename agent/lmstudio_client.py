from __future__ import annotations

from openai import OpenAI
from openai import APIConnectionError, APIError
from pydantic import ValidationError

from agent.config import LMStudioConfig
from agent.json_utils import extract_json_object
from agent.prompts import FALLBACK_JSON_INSTRUCTION, SYSTEM_PROMPT
from agent.schemas import AGENT_REPLY_JSON_SCHEMA, AgentContext, AgentReply


class LMStudioUnavailableError(RuntimeError):
    """Raised when the LM Studio local server cannot be reached."""


class LMStudioAgent:
    """
    Small LLM gateway for the robot mascot prototype.

    Responsibilities:
    - Send user text and app context to LM Studio.
    - Keep short conversation history.
    - Return structured output for UI, TTS, and mascot expression control.
    """

    def __init__(self, config: LMStudioConfig | None = None) -> None:
        self.config = config or LMStudioConfig()
        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
        )
        self.model = self.config.model or self._get_first_available_model()
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    def _get_first_available_model(self) -> str:
        try:
            models = self.client.models.list()
        except APIConnectionError as exc:
            raise LMStudioUnavailableError(
                "Could not connect to LM Studio. Start the LM Studio local server first."
            ) from exc
        except APIError as exc:
            raise LMStudioUnavailableError(
                f"LM Studio API error while listing models: {exc}"
            ) from exc

        if not models.data:
            raise LMStudioUnavailableError(
                "LM Studio is running, but no model is available. Load a model in LM Studio first."
            )

        return models.data[0].id

    def reset_history(self) -> None:
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    def ask(
        self,
        user_text: str,
        context: AgentContext | None = None,
    ) -> AgentReply:
        if not user_text or not user_text.strip():
            return AgentReply(
                reply="Please say or type something first.",
                expression="curious",
                tone="gentle",
                safety="safe",
                reason="Empty user input.",
            )

        context = context or AgentContext()
        user_message = self._build_user_message(user_text.strip(), context)

        try:
            result = self._ask_with_structured_output(user_message)
        except Exception:
            # Some smaller local models fail strict structured output.
            # Retry with a plain JSON instruction before falling back completely.
            try:
                result = self._ask_with_plain_json_prompt(user_message)
            except Exception:
                result = AgentReply(
                    reply="Sorry, I got a little confused. Could you say that again?",
                    expression="confused",
                    tone="gentle",
                    safety="safe",
                    reason="Model output could not be parsed into the required schema.",
                )

        self._save_turn(user_text.strip(), result.reply)
        return result

    def _build_user_message(self, user_text: str, context: AgentContext) -> str:
        parts = []

        if context.interaction_mode:
            parts.append(f"Interaction mode: {context.interaction_mode}")

        if context.user_mood:
            parts.append(f"Estimated user mood: {context.user_mood}")

        if context.extra_context:
            parts.append(f"Extra app context: {context.extra_context}")

        parts.append(f"User message: {user_text}")
        return "\n".join(parts)

    def _ask_with_structured_output(self, user_message: str) -> AgentReply:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history + [{"role": "user", "content": user_message}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format=AGENT_REPLY_JSON_SCHEMA,
        )
        content = completion.choices[0].message.content or ""
        data = extract_json_object(content)
        return AgentReply.model_validate(data)

    def _ask_with_plain_json_prompt(self, user_message: str) -> AgentReply:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
            + [
                {
                    "role": "user",
                    "content": f"{user_message}\n\n{FALLBACK_JSON_INSTRUCTION}",
                }
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        content = completion.choices[0].message.content or ""
        data = extract_json_object(content)

        try:
            return AgentReply.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Model returned invalid AgentReply JSON: {exc}") from exc

    def _save_turn(self, user_text: str, assistant_reply: str) -> None:
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": assistant_reply})

        max_messages = 1 + self.config.memory_turns * 2
        if len(self.history) > max_messages:
            self.history = [self.history[0]] + self.history[-self.config.memory_turns * 2 :]
