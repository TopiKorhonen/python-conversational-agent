from __future__ import annotations

from agent import AgentContext, LMStudioAgent
from agent.lmstudio_client import LMStudioUnavailableError


def main() -> None:
    try:
        agent = LMStudioAgent()
    except LMStudioUnavailableError as exc:
        print(f"LM Studio setup problem: {exc}")
        return

    print(f"LM Studio mascot agent ready. Using model: {agent.model}")
    print("Type 'exit' to stop. Type '/reset' to clear conversation memory.")

    while True:
        user_text = input("\nYou: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            break

        if user_text.lower() == "/reset":
            agent.reset_history()
            print("Conversation memory cleared.")
            continue

        result = agent.ask(
            user_text,
            context=AgentContext(
                user_mood="neutral",
                interaction_mode="text cli",
                extra_context="Testing the LM Studio gateway only.",
            ),
        )

        print(f"\nMascot: {result.reply}")
        print(f"Expression: {result.expression}")
        print(f"Tone: {result.tone}")
        print(f"Safety: {result.safety}")
        print(f"Reason: {result.reason}")


if __name__ == "__main__":
    main()
