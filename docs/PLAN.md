# Master Project Plan

## Project DamyDream — AI Communication Companion

---

## Executive Summary

Build a wearable AI communication system starting from a desktop prototype and evolving toward a wearable multilingual AI companion. The project prioritizes low-latency voice translation, offline edge inference, and incremental validation of conversational UX.

---

## Phased Execution Plan

### Phase 0 — Foundation Learning
**Duration:** 2–3 weeks
**Objective:** Learn core concepts needed for real-time AI audio systems.

| Topic | Key Concepts | Deliverable |
|---|---|---|
| Audio Engineering | Microphone streaming, Bluetooth audio routing, audio buffers, streaming pipelines, latency handling, VAD | Working audio capture/playback prototype |
| AI Inference | Whisper architecture, ONNX Runtime, quantization, edge AI inference, streaming AI | Benchmarked local inference pipeline |
| Mobile Development | Flutter basics, Android audio APIs, background services, permissions, Bluetooth integration | Simple Flutter audio recorder app |
| AI/LLM Concepts | Prompt engineering, conversational memory, context windows, streaming inference, local vs cloud inference | Memory-enabled chat prototype |

**Success Criteria:**
- Can capture and play back audio with < 100ms loopback latency
- Can run Whisper tiny locally in < 2s per utterance
- Understand VAD tuning parameters (thresholds, padding, min speech duration)

---

### Phase 1 — Desktop Prototype
**Duration:** 2–4 weeks
**Objective:** Create end-to-end local proof of concept on laptop.

**MVP Flow:**
```
Microphone Input → Speech-to-Text → Translation → Text-to-Speech → Speaker Output
```

**Features:**
- Real-time speech capture
- Multilingual translation
- Translated voice playback
- Simple UI
- Latency measurement logging

**Stack:**
- **Language:** Python
- **IDE:** VS Code
- **Libraries:** faster-whisper, sounddevice, torch, transformers, piper-tts, Silero VAD
- **Runtime:** ONNX Runtime

**Success Criteria:**
- Speak "Hello how are you" → hear translated Tamil/Japanese/etc audio
- Target latency: < 3 seconds end-to-end
- Works offline (no cloud calls)

---

### Phase 2 — Mobile MVP
**Duration:** 1–2 months
**Objective:** Move working pipeline to Android device.

**Architecture:**
```
Bluetooth Earbuds ↔ Android App ↔ Local AI Runtime ↔ Translation Pipeline
```

**Mandatory Features:**
- Bluetooth earbud support
- Microphone streaming
- Push-to-talk mode
- Conversation mode
- Translated speech playback
- Offline mode

**Optional Features:**
- Cloud inference fallback
- Transcript history

**Stack:**
- **Mobile:** Flutter
- **Android Native:** Kotlin modules for audio/Bluetooth
- **AI Runtime:** ONNX Runtime Mobile, llama.cpp, TensorFlow Lite
- **Models:** Whisper tiny/base, Meta NLLB, Piper TTS

**Success Criteria:**
- User speaks English → hears translated voice in earbuds
- Offline capable
- Latency < 2 seconds

---

### Phase 3 — AI Reply Assistant
**Duration:** 1–2 months
**Objective:** Add conversational intelligence.

**New Pipeline:**
```
Speech → Translation → Context Analysis → AI Reply Suggestions → User Approval → AI Voice Playback
```

**Features:**
- Quick AI reply suggestions
- Conversational memory
- Multilingual context awareness
- Meeting mode
- Travel mode

**LLM Options:**
- **Cloud:** OpenAI Realtime API, Gemini Live API, Claude API
- **Local:** Phi, Gemma, Qwen, Llama 3 small quantized

**Important Rule:** AI MUST NOT autonomously reply initially. User approval required.

---

### Phase 4 — Wearable AI Device
**Duration:** 3–6 months
**Objective:** Move toward dedicated wearable companion hardware.

**Possible Form Factors:**
- Wearable pendant
- Smart badge
- Clip-on microphone device
- Smartwatch companion
- Open-ear wearable

**Hardware Considerations:**
- Microphone array
- Battery optimization
- Thermal management
- Bluetooth Low Energy
- Edge inference capability

---

### Phase 5 — Autonomous Conversational Agent
**Duration:** Future / Advanced
**Objective:** Full autonomous multilingual conversation proxy.

**Features:**
- Autonomous multilingual response
- Emotional tone preservation
- Speaker identification
- Smart interruption handling
- Memory persistence
- Adaptive personality
- Context retention

---

## Timeline Summary

| Phase | Start | End | Duration | Cumulative |
|---|---|---|---|---|
| Phase 0 — Foundation | 2026-05-13 | 2026-06-03 | 3 weeks | 3 weeks |
| Phase 1 — Desktop MVP | 2026-06-03 | 2026-06-24 | 3 weeks | 6 weeks |
| Phase 2 — Mobile MVP | 2026-06-24 | 2026-08-24 | 2 months | 4.5 months |
| Phase 3 — AI Assistant | 2026-08-24 | 2026-10-24 | 2 months | 6.5 months |
| Phase 4 — Wearable | 2026-10-24 | 2027-02-24 | 4 months | 10.5 months |
| Phase 5 — Autonomous | 2027+ | TBD | TBD | TBD |

---

## Resource Requirements

### Personnel
- **Solo builder** (you) — AI architect, mobile engineer, audio engineer, product manager
- Optional: designer for Phase 3+ UX

### Development Environment
- Laptop (existing)
- Android flagship phone (Phase 2+)
- Bluetooth earbuds (Phase 2+)
- Optional: USB mic for desktop testing

---

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Latency > target | High | High | Optimize pipeline, use VAD aggressively, quantize models |
| Bluetooth instability | Medium | High | Test with multiple earbud brands, fallback to phone speaker |
| Noisy environment accuracy | High | High | Mic array, noise suppression, fine-tune VAD |
| Battery drain on mobile | Medium | Medium | Model quantization, efficient inference scheduling |
| Real-time sync issues | Medium | High | Buffer management, async pipeline, graceful degradation |

### Product Risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Awkward UX | Medium | High | Rapid user testing, iterate on interaction model |
| AI hallucinations | Medium | High | Restricted prompt templates, user approval gate |
| User trust issues | Medium | High | Transparent data handling, offline-first, privacy-first |
| Privacy concerns | Medium | High | All processing on-device, no cloud by default |
| Translation delays | High | High | Aggressive caching, streaming inference, short utterances |

---

## Evaluation Criteria for Phase Completion

Each phase must pass these gates before proceeding:

1. **Functional Gate:** Does the core flow work end-to-end?
2. **Latency Gate:** Does it meet the latency target?
3. **Reliability Gate:** Does it work in a noisy real-world environment?
4. **UX Gate:** Would a non-technical user find it natural?
5. **Offline Gate:** Does it work without internet?

---

## Definition of Done (Per Phase)

- [ ] Core pipeline functional end-to-end
- [ ] Latency measured and logged ( meets target )
- [ ] Works in at least one real-world test scenario (e.g., cafe, street)
- [ ] Documentation updated (architecture, API, usage)
- [ ] Decision log updated for any architectural choices
- [ ] Code committed and tagged: `phase-X-complete`

---

## Absolute Rules

1. **NO custom hardware** until Phase 4
2. **NO robotics** at any point in first 3 phases
3. **NO multi-agent orchestration** initially
4. **NO huge backend systems** early
5. **NO optimization for scale** before validation
6. **UX validation is mandatory** at every phase
7. **Measure latency continuously** — it is the primary metric
8. **Keep architecture simple** until Phase 3
