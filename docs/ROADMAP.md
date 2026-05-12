# Execution Roadmap

## EchoEcho-T — Clear Path from Idea to Product

---

## Roadmap Philosophy

This roadmap is a **living document**. It is designed to be:
- **Checkable:** Every milestone has a clear yes/no completion criteria
- **Sequential:** Later phases depend on earlier ones — no skipping
- **Measurable:** Latency is the primary metric; UX is the secondary metric
- **Pragmatic:** If something doesn't work, we stop and fix it before advancing

---

## Phase 0 — Foundation Learning (Weeks 1–3)

### Week 1: Audio Engineering
- [ ] Set up Python audio environment (sounddevice, PyAudio)
- [ ] Build audio loopback test (capture → immediate playback)
- [ ] Measure and log baseline latency
- [ ] Study Silero VAD: run examples, tune thresholds
- [ ] Learn audio buffer management (chunk sizes, streaming)
- [ ] **Checkpoint:** Working audio capture/playback with < 100ms loopback latency

### Week 2: AI Inference
- [ ] Set up ONNX Runtime environment
- [ ] Download and run Whisper tiny locally
- [ ] Measure inference time on your laptop
- [ ] Study quantization: FP32 → FP16 → INT8
- [ ] Run a basic STT → translation → TTS pipeline manually
- [ ] **Checkpoint:** Can transcribe, translate, and speak a sentence end-to-end

### Week 3: Mobile + LLM Foundations
- [ ] Install Flutter, create sample app
- [ ] Build simple audio recorder in Flutter (or prototype in native)
- [ ] Learn Android audio service lifecycle
- [ ] Study prompt engineering basics
- [ ] Build a simple memory-enabled chatbot (local or cloud)
- [ ] **Checkpoint:** Can build a basic mobile UI and understand LLM context windows

### Phase 0 Gate
**Required to proceed:**
- [ ] Audio latency measured and < 100ms loopback
- [ ] Whisper tiny runs in < 2s on your laptop
- [ ] Understand VAD parameters and can tune them
- [ ] Basic Flutter app skeleton running on Android emulator or device

---

## Phase 1 — Desktop Prototype (Weeks 4–6)

### Week 4: Pipeline Construction
- [ ] Implement audio capture module (streaming chunks)
- [ ] Integrate Silero VAD for speech detection
- [ ] Implement STT module (faster-whisper or ONNX)
- [ ] **Checkpoint:** Speak → get transcript reliably

### Week 5: Translation + TTS
- [ ] Integrate translation module (NLLB or Argos)
- [ ] Integrate TTS module (Piper)
- [ ] Wire full pipeline: Audio → VAD → STT → Translation → TTS → Audio
- [ ] Add simple desktop UI (start/stop, language select, status)
- [ ] **Checkpoint:** Full pipeline works end-to-end

### Week 6: Optimization + Hardening
- [ ] Add latency logging per stage
- [ ] Optimize buffer sizes for your hardware
- [ ] Test in noisy environment (cafe, street, car)
- [ ] Add push-to-talk mode as fallback
- [ ] Document latency measurements
- [ ] **Checkpoint:** Latency < 3s, works in real-world noise

### Phase 1 Gate
**Required to proceed:**
- [ ] Speak "Hello how are you" → hear translated Tamil/Japanese/etc audio
- [ ] End-to-end latency < 3 seconds consistently
- [ ] Works offline (no cloud calls)
- [ ] Tested in at least one noisy real-world environment
- [ ] Tag: `phase-1-complete`

---

## Phase 2 — Mobile MVP (Months 3–4)

### Month 3, Week 1: Flutter + Audio Foundation
- [ ] Set up Flutter project with Kotlin modules
- [ ] Implement Android audio capture service (foreground)
- [ ] Implement audio playback via AAudio/Oboe
- [ ] **Checkpoint:** Audio I/O works in Flutter app

### Month 3, Week 2: Model Porting
- [ ] Convert Whisper to ONNX Runtime Mobile format
- [ ] Convert NLLB to mobile-compatible format
- [ ] Convert Piper voices to ONNX
- [ ] Test inference on target Android device
- [ ] **Checkpoint:** All models run on Android phone

### Month 3, Week 3: Pipeline Integration
- [ ] Port desktop pipeline to mobile (Kotlin or FFI)
- [ ] Integrate VAD for mobile streaming
- [ ] Wire STT → Translation → TTS on device
- [ ] Add language pair selection UI
- [ ] **Checkpoint:** Mobile pipeline works end-to-end

### Month 3, Week 4: Bluetooth + Modes
- [ ] Implement Bluetooth earbud audio routing
- [ ] Test with at least 2 earbud brands
- [ ] Implement push-to-talk mode
- [ ] Implement conversation mode (auto-detect turns)
- [ ] **Checkpoint:** Bluetooth audio I/O works reliably

### Month 4, Week 1: Offline + Optimization
- [ ] Verify full offline operation (airplane mode)
- [ ] Optimize model loading (lazy init, caching)
- [ ] Reduce latency: target < 2s
- [ ] Add transcript history (optional)
- [ ] **Checkpoint:** Offline capable, latency < 2s

### Month 4, Week 2: Polish + Real-World Testing
- [ ] UI polish: language flags, status indicators, latency display
- [ ] Real-world testing: 5+ conversations with real humans
- [ ] Gather feedback, identify UX pain points
- [ ] Document issues and resolutions
- [ ] **Checkpoint:** Non-technical users can operate it

### Phase 2 Gate
**Required to proceed:**
- [ ] User speaks English → hears translated voice in earbuds
- [ ] Offline capable (airplane mode)
- [ ] Latency < 2 seconds consistently
- [ ] Works with at least 2 Bluetooth earbud models
- [ ] Tested with 5+ real human conversations
- [ ] Tag: `phase-2-complete`

---

## Phase 3 — AI Reply Assistant (Months 5–6)

### Month 5, Week 1: LLM Integration
- [ ] Integrate small local LLM (Phi-3-mini, Gemma-2B, or Qwen-1.5B)
- [ ] Build prompt template for reply suggestions
- [ ] Implement context window management
- [ ] Test on Android device (performance check)
- [ ] **Checkpoint:** LLM generates reply suggestions locally

### Month 5, Week 2: Context + Memory
- [ ] Implement conversation memory (sliding window)
- [ ] Add speaker identification (basic)
- [ ] Build context-aware prompt injection
- [ ] Add meeting mode (formal tone, no slang)
- [ ] Add travel mode (common phrases, directions)
- [ ] **Checkpoint:** AI replies are contextually relevant

### Month 5, Week 3: Approval Flow
- [ ] Implement user approval UI (suggestion cards)
- [ ] Add quick-approve gestures (tap to speak)
- [ ] Implement reject + regenerate flow
- [ ] Add "always ask" vs "suggest only" settings
- [ ] **Checkpoint:** User can approve/reject AI replies easily

### Month 5, Week 4: Voice + Polish
- [ ] AI replies spoken via TTS after approval
- [ ] Add emotional tone selection (formal, friendly, urgent)
- [ ] Cloud fallback for complex queries (opt-in)
- [ ] UI for mode selection (meeting, travel, casual)
- [ ] **Checkpoint:** Full AI reply pipeline works

### Month 6, Weeks 1–2: Testing + Refinement
- [ ] Test AI replies in 10+ real conversations
- [ ] Measure hallucination rate (target < 5%)
- [ ] Optimize LLM inference speed (quantization, caching)
- [ ] Add feedback mechanism (thumbs up/down on replies)
- [ ] Document accuracy and UX findings
- [ ] **Checkpoint:** AI replies are helpful and trustworthy

### Phase 3 Gate
**Required to proceed:**
- [ ] AI suggests contextually relevant replies
- [ ] User approval gate works smoothly
- [ ] Hallucination rate < 5% (measured)
- [ ] Latency for AI reply < 3s (inference + approval + TTS)
- [ ] Tag: `phase-3-complete`

---

## Phase 4 — Wearable Device (Months 7–10)

### Month 7: Hardware Research
- [ ] Research wearable form factors (pendant, badge, clip-on)
- [ ] Evaluate dev kits: ESP32-S3, Raspberry Pi Zero 2W, Qualcomm QCS
- [ ] Select microphone arrays (Knowles, InvenSense)
- [ ] Battery + thermal analysis
- [ ] **Checkpoint:** Hardware platform selected

### Month 8: Prototype Build
- [ ] Assemble first wearable prototype (breadboard or dev kit)
- [ ] Implement BLE peripheral (audio streaming to phone)
- [ ] Test audio quality vs. phone mic
- [ ] Battery life benchmarking (target: 4+ hours)
- [ ] **Checkpoint:** Wearable streams audio to phone reliably

### Month 9: Integration
- [ ] Integrate wearable audio stream into mobile pipeline
- [ ] Optimize for wearable-specific audio characteristics
- [ ] Add wearable UI (LED indicators, haptics)
- [ ] Test end-to-end: wearable mic → phone AI → earbuds out
- [ ] **Checkpoint:** Full wearable loop works

### Month 10: Refinement + DFM Prep
- [ ] Industrial design concepts
- [ ] PCB design (if custom)
- [ ] Battery optimization (deep sleep, wake-on-voice)
- [ ] Durability testing
- [ ] Cost analysis for manufacturing
- [ ] **Checkpoint:** Wearable prototype is daily-usable

### Phase 4 Gate
**Required to proceed:**
- [ ] Wearable device streams audio to phone reliably
- [ ] Battery life > 4 hours continuous use
- [ ] Audio quality comparable to phone mic
- [ ] Cost estimate for 100-unit manufacturing
- [ ] Tag: `phase-4-complete`

---

## Phase 5 — Autonomous Conversational Agent (Future)

**Not scheduled. Will be planned after Phase 4 evaluation.**

Potential features:
- Autonomous reply mode (with user-configurable trust levels)
- Emotional tone preservation across translation
- Persistent memory across conversations
- Adaptive personality based on user feedback
- Smart interruption handling

---

## Go/No-Go Decision Points

| Point | Date | Question | Proceed If |
|---|---|---|---|
| Phase 0→1 | 2026-06-03 | Can we build basic audio + AI pipeline? | Latency < 2s on laptop |
| Phase 1→2 | 2026-06-24 | Does desktop prototype work in real world? | Latency < 3s, tested with humans |
| Phase 2→3 | 2026-08-24 | Does mobile MVP work reliably? | Latency < 2s, Bluetooth stable, 5+ real tests |
| Phase 3→4 | 2026-10-24 | Are AI replies valuable? | < 5% hallucination, users find helpful |
| Phase 4→5 | 2027-02-24 | Is wearable form factor viable? | Daily usable, battery > 4h, cost viable |

---

## Parallel Workstreams

While the main roadmap is sequential, these can happen in parallel once Phase 1 is complete:

- **Design:** UI/UX exploration for mobile app (ongoing from Phase 1)
- **Community:** Open-source the Phase 1 pipeline (optional, after validation)
- **Business:** Cost analysis, pricing model, manufacturing quotes (Phase 3+)
- **Research:** Follow latest edge AI papers (Whisper streaming, tiny LLMs)

---

## Dependencies & External Factors

| Dependency | Risk | Mitigation |
|---|---|---|
| ONNX Runtime Mobile stability | Medium | Test early on target device; fallback to TFLite |
| Flutter + Kotlin audio bridge | Medium | Prototype audio in Kotlin first, then bridge |
| Model availability for target language | Medium | Prioritize top 10 languages; use cloud fallback for rare |
| Bluetooth audio routing on Android | High | Test with multiple earbud brands; use phone speaker fallback |
| Android background service limits | Medium | Use foreground service with persistent notification |

---

## How to Use This Roadmap

1. **Weekly:** Check tasks/todo.md against current phase milestones
2. **Phase-end:** Run the gate checklist before advancing
3. **Blocked?** Document in tasks/todo.md, do not skip ahead
4. **Ahead of schedule?** Use time for optimization or parallel workstreams
5. **Behind schedule?** Cut optional features, not core pipeline stages

---

## Success Metric Reminder

> The first milestone is NOT "AI ecosystem"
>
> The first milestone is: User speaks English → translated voice plays smoothly → conversation feels natural → latency acceptable → works reliably in real-world environments

Validate this at every phase gate.
