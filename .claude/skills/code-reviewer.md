---
name: code-reviewer
description: Military-grade code review, security audit, unit/integration testing, and QA validation for EchoEcho-T
version: 1.0.0
---

# Code Reviewer — Military-Grade Quality Gate

## Activation
- User says "review this code", "security scan", "run tests", "QA this", "audit the pipeline"
- Before ANY commit to `main`
- After any bug fix before calling it done
- When user requests "military level testing"

## Mission
Zero-defect delivery. Every line of code, every model output, every audio pipeline stage must be validated before it reaches the user.

---

## Phase 1 — Static Analysis (Read-Only)

### 1.1 Code Hygiene Checklist
- [ ] No hardcoded secrets, API keys, tokens, or credentials
- [ ] No `print()` in production code — use structured logging
- [ ] No broad `except:` or `except Exception:` without specific handling
- [ ] All file paths use `os.path` or `pathlib`, no string concatenation
- [ ] All threads have names (`name="Worker-X"`), all daemons are intentional
- [ ] No infinite loops without exit conditions or timeouts
- [ ] No mutable default arguments in function signatures
- [ ] All imports at top of file, no dynamic imports inside hot paths

### 1.2 Security Audit
- [ ] Input validation on ALL user-facing interfaces (CLI args, audio chunks, STT text)
- [ ] No SQL injection vectors (if any DB code exists)
- [ ] No command injection via `os.system`, `subprocess.call` with user input
- [ ] No path traversal via unvalidated file names
- [ ] No unsafe deserialization (`pickle`, `yaml.load` without `SafeLoader`)
- [ ] No unvalidated model downloads (check `trust_repo`, signature verification)
- [ ] Error messages sanitized — no stack traces or internal paths leaked to user
- [ ] Rate limiting / queue bounds on all async paths

### 1.3 Architecture Review
- [ ] Single responsibility per module
- [ ] No circular imports
- [ ] Queue sizes bounded (`maxsize=`) to prevent memory explosions
- [ ] Thread lifecycle managed (start, stop, join with timeout)
- [ ] Resource cleanup in `__exit__` / `finally` / context managers
- [ ] No global mutable state

---

## Phase 2 — Dynamic Testing (Execution Required)

### 2.1 Unit Tests (Every Function)
```python
# For EVERY public function, verify:
- Happy path returns expected type
- Empty input handled gracefully
- Invalid input raises correct exception
- Boundary conditions (max length, empty queue, timeout)
- Idempotency (same input → same output)
```

### 2.2 Integration Tests (Pipeline Stages)
```python
# For every pipeline stage pair:
- AudioCapture → VAD (real mic or mock WAV)
- VAD → STT (pre-recorded speech segments)
- STT → LanguageManager (known utterances)
- LanguageManager → TTS (all 15 languages)
- TTS → Speaker (verify audio output not None)
```

### 2.3 End-to-End Tests (Full Pipeline)
```python
# Test vectors:
- "Hello" → German "Hallo"
- "How are you" → Tamil "நீங்கள் எப்படி இருக்கிறீர்கள்"
- "switch to Japanese" → Japanese confirmation TTS
- Silence → no output, no crash
- Loud noise → VAD rejects, no STT attempt
- Rapid speech → all words captured, no truncation
```

### 2.4 Stress Tests
- [ ] 100 rapid utterances back-to-back — no queue overflow
- [ ] 5-minute continuous run — no memory leak
- [ ] Language switch 10 times in 30 seconds — stable
- [ ] Interruption (Ctrl+C) at random moments — clean shutdown
- [ ] TTS feedback loop test: mic picks up speaker → cooldown works

### 2.5 Regression Tests
- [ ] Re-run ALL previous failing test cases before declaring fix
- [ ] Compare output against golden files where applicable
- [ ] Verify no new warnings in logs

---

## Phase 3 — QA Verdict

### Scoring Matrix (0-10 per category)

| Category | Weight | Score | Notes |
|----------|--------|-------|-------|
| Correctness | 30% | _ | Output matches expected for all test vectors |
| Security | 20% | _ | No vulnerabilities, sanitized errors, bounded queues |
| Performance | 15% | _ | Latency within budget, no memory leaks |
| Reliability | 15% | _ | Handles edge cases, graceful degradation |
| Maintainability | 10% | _ | Clean code, tests pass, docs current |
| Usability | 10% | _ | Clear error messages, intuitive CLI |

### Final Verdict
- **PASS (≥ 8.0 average)**: Ready for merge
- **CONDITIONAL PASS (6.0-7.9)**: Merge with documented follow-ups
- **FAIL (< 6.0)**: Block merge, fix and re-review

### Sign-Off Format
```
[QA VERDICT] {PASS | CONDITIONAL PASS | FAIL}
Score: {X.X}/10
Blockers: {list}
Warnings: {list}
Follow-ups: {list}
```

---

## Phase 4 — Test Case Switching

When user says "switch test mode to {mode}":

### Modes
1. **smoke** — 3 quick tests, 10 seconds
2. **unit** — All unit tests, fast
3. **integration** — Stage-to-stage tests, medium
4. **e2e** — Full pipeline with real audio, slow
5. **stress** — 100+ iterations, memory profiling
6. **regression** — All historical bug reproductions
7. **military** — ALL of the above + fuzzing + adversarial inputs

### Military Mode Extra Checks
- Fuzz STT input with random Unicode
- Fuzz audio with white noise, sine waves, silence
- Inject corrupted model weights (simulate failure)
- Run under `valgrind` / `tracemalloc` for leaks
- Verify no network calls during offline operation

---

## Execution Rules
- NEVER skip a failing test by commenting it out
- NEVER reduce test coverage to make tests pass
- ALWAYS run tests on the actual changed code, not stubs
- ALWAYS test on both CPU and GPU if GPU code exists
- ALWAYS test all 15 languages for translation changes
- ALWAYS test real microphone path before declaring audio code done
