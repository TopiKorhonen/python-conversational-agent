from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


Expression = Literal[
    "neutral",
    "happy",
    "curious",
    "thinking",
    "concerned",
    "sad",
    "surprised",
    "confused",
]

Tone = Literal[
    "normal",
    "cheerful",
    "gentle",
    "calm",
    "curious",
]

SafetyLevel = Literal[
    "safe",
    "caution",
    "refuse",
]


class AgentContext(BaseModel):
    """Optional context that other modules can pass to the LLM gateway later."""

    user_mood: str | None = Field(
        default=None,
        description="Mood estimate from face/voice modules, for example: neutral, happy, sad, angry.",
    )
    interaction_mode: str | None = Field(
        default="text",
        description="Interaction source, for example: text, voice, demo, testing.",
    )
    extra_context: str | None = Field(
        default=None,
        description="Any short context string from the app.",
    )


class AgentReply(BaseModel):
    """Structured response returned by the LLM gateway."""

    reply: str = Field(description="The user-facing answer that can be shown or spoken.")
    expression: Expression = Field(description="Suggested mascot face expression.")
    tone: Tone = Field(description="Suggested speaking style for text-to-speech later.")
    safety: SafetyLevel = Field(description="Safety classification of the response.")
    reason: str = Field(
        default="",
        description="Brief internal explanation for why the expression/tone was chosen.",
    )


AGENT_REPLY_JSON_SCHEMA: dict = {
    "type": "json_schema",
    "json_schema": {
        "name": "mascot_agent_reply",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "reply": {"type": "string"},
                "expression": {
                    "type": "string",
                    "enum": [
                        "neutral",
                        "happy",
                        "curious",
                        "thinking",
                        "concerned",
                        "sad",
                        "surprised",
                        "confused",
                    ],
                },
                "tone": {
                    "type": "string",
                    "enum": ["normal", "cheerful", "gentle", "calm", "curious"],
                },
                "safety": {
                    "type": "string",
                    "enum": ["safe", "caution", "refuse"],
                },
                "reason": {"type": "string"},
            },
            "required": ["reply", "expression", "tone", "safety", "reason"],
            "additionalProperties": False,
        },
    },
}
