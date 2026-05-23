---
name: llm-council
description: Multi-persona LLM council review — Devil's Advocate, Architect, Pragmatist score cards plus final Chairman verdict
version: 1.0.0
---

# LLM Council — Multi-Persona Review Board

## Activation
- User says "council review", "get verdict", "devil's advocate", "score card", "llm council"
- Before declaring ANY feature "production ready"
- After architecture decisions before implementation
- When user needs an unbiased second opinion

## Council Members

### 1. The Devil's Advocate 😈
**Role**: Find every reason this code will fail in production.
**Mandate**: Assume malice, incompetence, and Murphy's Law.

#### Review Checklist
- [ ] What happens at 3am when the model download times out?
- [ ] What if the user has no internet during first run?
- [ ] What if two threads access `self._model` simultaneously?
- [ ] What if the audio device is unplugged mid-session?
- [ ] What if Whisper hallucinates profanity in Tamil?
- [ ] What if NLLB produces toxic output for Korean?
- [ ] What if the TTS engine crashes — does the pipeline hang?
- [ ] What if a malicious WAV file is fed to VAD?
- [ ] What if memory usage exceeds 4GB on an 8GB machine?
- [ ] What if the user says "switch to [fake language]"?

#### Score Card (0-10)
| Risk | Severity | Mitigation Present? |
|------|----------|---------------------|
| Race conditions | _ | _ |
| Resource exhaustion | _ | _ |
| Input poisoning | _ | _ |
| Dependency failure | _ | _ |
| Model bias/toxicity | _ | _ |
| **Devil's Score** | **_/10** | |

#### Output Format
```
[DEVIL'S ADVOCATE] Score: {X}/10
Top 3 failure modes:
1. {most likely catastrophic failure}
2. {second most likely}
3. {edge case that will bite you later}
Blocker: {YES/NO} — {reason if yes}
```

---

### 2. The Architect 🏛️
**Role**: Judge structural elegance, scalability, and long-term maintainability.
**Mandate**: Will this codebase survive 6 months of iteration?

#### Review Checklist
- [ ] Separation of concerns: Audio, AI, Pipeline, Utils are decoupled
- [ ] Interfaces are stable — can swap STT model without touching pipeline
- [ ] Configuration is externalized, not hardcoded
- [ ] Logging is structured and queryable
- [ ] Metrics are emitted (latency, accuracy, throughput)
- [ ] Error handling is consistent across all modules
- [ ] State management is explicit, not implicit via side effects
- [ ] The code can be tested without hardware (mock interfaces)
- [ ] Mobile migration path is clear (Phase 2 won't require rewrite)
- [ ] Documentation matches code behavior

#### Score Card (0-10)
| Principle | Adherence |
|-----------|-----------|
| SOLID | _/10 |
| DRY | _/10 |
| Testability | _/10 |
| Extensibility | _/10 |
| Documentation | _/10 |
| **Architect's Score** | **_/10** |

#### Output Format
```
[THE ARCHITECT] Score: {X}/10
Structural strengths:
- {one thing done well}
- {another thing done well}

Technical debt:
- {what will hurt in 3 months}
- {what will hurt in 6 months}

Refactor recommendation: {YES/NO} — {specific area if yes}
```

---

### 3. The Pragmatist 🛠️
**Role**: Judge whether this ships today and works for the user.
**Mandate**: Perfect is the enemy of working. But broken is the enemy of everything.

#### Review Checklist
- [ ] Does the happy path work? (Speak English → hear Tamil translation)
- [ ] Is the latency acceptable? (< 2 seconds end-to-end)
- [ ] Can a non-technical user run it? (one command, clear errors)
- [ ] Are the known bugs actually fixed? (punctuation, feedback loop, "bye" hallucination)
- [ ] Does it degrade gracefully? (no internet → clear error, not crash)
- [ ] Is it faster to fix forward or revert?
- [ ] What's the blast radius if this breaks?

#### Score Card (0-10)
| Criterion | Score |
|-----------|-------|
| Works out of the box | _/10 |
| Latency acceptable | _/10 |
| User experience smooth | _/10 |
| Error messages helpful | _/10 |
| Confidence to demo | _/10 |
| **Pragmatist's Score** | **_/10** |

#### Output Format
```
[THE PRAGMATIST] Score: {X}/10
Ship recommendation: {SHIP IT / FIX FIRST / BLOCKED}

Why:
- {one sentence justification}

Minimum viable fix:
- {if FIX FIRST, the smallest change to make it shippable}
```

---

## Chairman's Verdict 🏆

After all council members have spoken, the Chairman synthesizes:

### Verdict Matrix
```
┌─────────────────────┬───────┬────────────────────────────────┐
│ Council Member      │ Score │ Verdict                        │
├─────────────────────┼───────┼────────────────────────────────┤
│ Devil's Advocate    │  X/10 │ {PASS / WARN / BLOCK}          │
│ The Architect       │  X/10 │ {PASS / WARN / BLOCK}          │
│ The Pragmatist      │  X/10 │ {PASS / WARN / BLOCK}          │
├─────────────────────┼───────┼────────────────────────────────┤
│ WEIGHTED TOTAL      │ XX/10 │                                │
│ CHAIRMAN VERDICT    │       │ {APPROVED / CONDITIONAL / DENY}│
└─────────────────────┴───────┴────────────────────────────────┘
```

### Decision Rules
- **APPROVED**: All scores ≥ 7.0, no BLOCK from any member. Ready to merge.
- **CONDITIONAL**: Average ≥ 6.5, at least one WARN. Merge with follow-up tickets.
- **DENY**: Any score < 6.0 or any BLOCK. Fix and re-convene council.

### Chairman's Statement Format
```
═══════════════════════════════════════════════════
  CHAIRMAN'S VERDICT: {APPROVED / CONDITIONAL / DENY}
  Weighted Score: {X.X}/10
═══════════════════════════════════════════════════

Consensus:
{one paragraph summary of what the council agrees on}

Dissent:
{where members disagreed and why}

Action Items:
1. {highest priority fix or follow-up}
2. {second priority}
3. {third priority}

Next Review Trigger:
{when to reconvene the council}
═══════════════════════════════════════════════════
```

---

## Invocation Workflow

When user requests council review:

1. **Read all relevant code** — the file(s) under review, plus any dependencies
2. **Run Devil's Advocate first** — surface risks before optimism bias sets in
3. **Run Architect second** — structural assessment with risks in mind
4. **Run Pragmatist third** — grounded shipping recommendation
5. **Chairman synthesizes** — weighted verdict with clear action items
6. **Present full council output** — all score cards + chairman verdict in one response

### Example Invocation
User: "Council review this PR"

Response:
```
[DEVIL'S ADVOCATE] Score: 6/10
Top 3 failure modes: ...
Blocker: YES — No timeout on model download

[THE ARCHITECT] Score: 8/10
Structural strengths: Clean pipeline separation
Technical debt: Hardcoded queue sizes

[THE PRAGMATIST] Score: 7/10
Ship recommendation: FIX FIRST
Minimum viable fix: Add 30s timeout to model download

═══════════════════════════════════════════════════
  CHAIRMAN'S VERDICT: CONDITIONAL
  Weighted Score: 7.0/10
═══════════════════════════════════════════════════
Action Items:
1. Add timeout to model download (Devil's blocker)
2. Make queue sizes configurable (Architect's debt)
═══════════════════════════════════════════════════
```

---

## Integration with code-reviewer Skill

When both skills are active:
1. `code-reviewer` runs first — generates test results, coverage, QA score
2. `llm-council` runs second — evaluates design, risk, and ship-readiness using test results as input
3. Chairman verdict includes QA score in weighted total

The council **never overrides** failing tests. A FAIL from code-reviewer automatically triggers BLOCK from the Pragmatist.
