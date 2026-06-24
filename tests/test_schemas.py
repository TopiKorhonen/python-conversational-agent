from agent.schemas import AgentReply


def test_agent_reply_schema_accepts_valid_data() -> None:
    reply = AgentReply(
        reply="Hello! How can I help?",
        expression="happy",
        tone="cheerful",
        safety="safe",
        reason="Friendly greeting.",
    )

    assert reply.expression == "happy"
    assert reply.safety == "safe"
