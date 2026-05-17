# Phase 0 — LLM Foundations (Week 3)

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| `memory_chat.py` | Conversational memory + prompt engineering demo | `python memory_chat.py` |

## Quick Start

```bash
python memory_chat.py
```

Commands during chat:
- Type normally to chat
- `history` — Show conversation memory
- `prompt` — Show full prompt being built
- `quit` / `exit` / `bye` — End session

## Key Concepts Demonstrated

1. **System Prompt:** Defines AI personality and constraints
2. **Conversation History:** Sliding window of last N turns
3. **Context Window:** Simulated 4K token limit with enforcement
4. **Prompt Builder:** Concatenates system + history + user message
5. **Token Estimation:** Rough count for context management

## How This Maps to Phase 3

| Concept | Phase 0 (Learning) | Phase 3 (Real Implementation) |
|---|---|---|
| LLM | Rule-based simulation | Phi-3-mini / Gemma-2B via llama.cpp |
| Memory | Python list | SQLite / Hive local storage |
| Context window | Simulated 4K | Real tokenizer (BPE) |
| Streaming | Simulated typing | Real token-by-token generation |
| Prompt builder | String concat | Template engine with Jinja2 |

## Prompt Engineering Patterns

```
System: [Personality + constraints]

User: [message 1]
Assistant: [response 1]

User: [message 2]
Assistant: [response 2]

User: [current message]
Assistant:
```

This is the standard chat format used by:
- OpenAI ChatGPT
- Claude
- Llama / Phi / Gemma

## Context Window Management

- **Sliding window:** Drop oldest turns when limit reached
- **Summarization:** (Future) Compress old turns into summary
- **Token counting:** Essential to prevent overflow

## Next Step

After this works, we'll:
1. Replace simulated responses with real local LLM (llama.cpp)
2. Add reply suggestion mode (not free chat)
3. Add approval flow UI
4. Implement persistent storage
