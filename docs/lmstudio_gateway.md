# LM Studio LLM Gateway

This module provides the local LLM conversation layer for the robot mascot prototype.

## Purpose

The LLM gateway receives user text and optional context from the rest of the application. It sends the request to LM Studio through the local OpenAI-compatible API and returns a structured result.

The result contains:

- `reply`: the text answer to show or speak
- `expression`: suggested mascot face expression
- `tone`: suggested response tone for future text-to-speech integration
- `safety`: simple safety category
- `reason`: short explanation of the chosen response style

## Setup

1. Open LM Studio.
2. Download and load an instruct/chat model.
3. Start the local server.
4. Make sure the local URL is available, usually:

```text
http://localhost:1234/v1
```

5. Copy `.env.example` to `.env`.
6. Optionally set `LMSTUDIO_MODEL` to the exact model id shown in LM Studio.

## Install dependencies with uv

```bash
uv add openai pydantic python-dotenv streamlit
```

Or, if your team uses requirements files:

```bash
uv pip install -r requirements-lmstudio.txt
```

## Run CLI test

```bash
uv run python app_lmstudio_cli.py
```

## Run Streamlit test

```bash
uv run streamlit run streamlit_lmstudio_demo.py
```

## Integration point for teammates

Other modules can call:

```python
from agent import AgentContext, LMStudioAgent

agent = LMStudioAgent()

result = agent.ask(
    "Can you help me?",
    context=AgentContext(
        user_mood="sad",
        interaction_mode="voice",
        extra_context="Speech-to-text module produced this message.",
    ),
)

print(result.reply)
print(result.expression)
print(result.tone)
```

## Limitations

- Local model quality depends heavily on the loaded model.
- Small models may not always follow structured JSON output.
- The gateway includes a fallback JSON parser, but it is not perfect.
- Safety handling is basic and should be improved before any public use.
- The agent should not claim to be a real child or human.
- Mood input is treated as an estimate, not a fact.
