import time

"""
Memory-Enabled Chat — Phase 0, Week 3

Demonstrates:
- Prompt engineering basics
- Conversational memory (sliding window)
- Context window management
- Streaming LLM output simulation

Usage:
    python memory_chat.py
"""

MAX_HISTORY = 10  # Keep last N turns to stay within context window
SYSTEM_PROMPT = """You are EchoEcho-T, a helpful AI communication assistant.
You help users practice conversations and suggest natural replies.
Keep responses brief (1-2 sentences). Be friendly and practical."""


def simulate_llm_response(user_message: str, history: list) -> str:
    """
    Simulates an LLM response.
    In Phase 3, this will call a real local LLM (Phi-3, Gemma, etc.).
    For now, we use a rule-based simulation to learn the pattern.
    """
    msg = user_message.lower()

    if "hello" in msg or "hi" in msg:
        return "Hello! Ready to practice some conversation?"
    if "translate" in msg:
        return "I can help with that! What language would you like to translate to?"
    if "thank" in msg:
        return "You're welcome! Let me know if you need anything else."
    if "bye" in msg or "goodbye" in msg:
        return "Goodbye! Have a great conversation!"
    if "help" in msg:
        return "I can suggest replies, translate, or help you practice conversations. What do you need?"

    return "Interesting! Tell me more about that."


def build_prompt(system: str, history: list, user_message: str) -> str:
    """
    Build a formatted prompt with system instructions and conversation history.
    This is the core prompt engineering pattern we'll use with real LLMs.
    """
    prompt_parts = [f"System: {system}", ""]

    for turn in history:
        prompt_parts.append(f"User: {turn['user']}")
        prompt_parts.append(f"Assistant: {turn['assistant']}")
        prompt_parts.append("")

    prompt_parts.append(f"User: {user_message}")
    prompt_parts.append("Assistant:")

    return "\n".join(prompt_parts)


def count_tokens(text: str) -> int:
    """
    Rough token count (1 token ≈ 4 chars for English).
    Real LLMs use BPE tokenizers; this is an approximation for learning.
    """
    return len(text) // 4


def main():
    print("=" * 60)
    print("Memory-Enabled Chat — EchoEcho-T")
    print("=" * 60)
    print(f"System prompt: {SYSTEM_PROMPT[:60]}...")
    print(f"Max history:   {MAX_HISTORY} turns")
    print(f"Context limit: Simulated 4K tokens")
    print("-" * 60)
    print("Type your message. Type 'quit', 'exit', or 'bye' to end.")
    print("Type 'history' to see conversation memory.")
    print("Type 'prompt' to see the full prompt being built.")
    print("-" * 60)

    history = []
    total_turns = 0

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print("Goodbye!")
            break

        if user_input.lower() == "history":
            print(f"\n--- Conversation History ({len(history)} turns) ---")
            for i, turn in enumerate(history, 1):
                print(f"{i}. You: {turn['user'][:40]}...")
                print(f"   AI:  {turn['assistant'][:40]}...")
            continue

        if user_input.lower() == "prompt":
            prompt = build_prompt(SYSTEM_PROMPT, history, "[example message]")
            tokens = count_tokens(prompt)
            print(f"\n--- Current Prompt ({tokens} est. tokens) ---")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            print(f"\nEstimated tokens: {tokens} / 4096")
            continue

        # Simulate streaming response
        t0 = time.time()
        response = simulate_llm_response(user_input, history)
        elapsed = time.time() - t0

        # Display with simulated typing effect
        print("AI:  ", end="", flush=True)
        for char in response:
            print(char, end="", flush=True)
            time.sleep(0.01)  # Simulate streaming
        print(f"  [{elapsed*1000:.0f}ms]")

        # Store in memory
        history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": time.time(),
        })
        total_turns += 1

        # Enforce sliding window
        if len(history) > MAX_HISTORY:
            removed = history.pop(0)
            print(f"  [Memory: oldest turn removed to stay within context window]")

        # Show memory stats
        prompt_preview = build_prompt(SYSTEM_PROMPT, history, "...")
        tokens = count_tokens(prompt_preview)
        print(f"  [Context: {tokens} est. tokens | Turns: {len(history)}/{MAX_HISTORY}]")

    print("\n" + "=" * 60)
    print(f"Session complete: {total_turns} turns")
    print(f"Final history:    {len(history)} turns kept")
    print("=" * 60)


if __name__ == "__main__":
    main()
