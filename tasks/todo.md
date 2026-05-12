# Current Tasks

## EchoEcho-T — Sprint Tracker

---

## Active Phase: Phase 0 — Foundation Learning

### Week 1: Audio Engineering (2026-05-13 → 2026-05-20)

- [ ] Set up Python audio environment (sounddevice, numpy)
- [ ] Build audio loopback test script
- [ ] Measure and log baseline latency
- [ ] Download and test Silero VAD
- [ ] Tune VAD thresholds for your environment
- [ ] Document audio buffer findings
- [ ] **Checkpoint:** Working audio capture/playback with < 100ms loopback latency

### Week 2: AI Inference (2026-05-20 → 2026-05-27)

- [ ] Install ONNX Runtime
- [ ] Download Whisper tiny
- [ ] Build STT benchmark script
- [ ] Measure inference time on your laptop
- [ ] Test quantization (FP16 vs INT8)
- [ ] Manually run STT → translate → TTS chain
- [ ] **Checkpoint:** Can transcribe, translate, and speak a sentence end-to-end

### Week 3: Mobile + LLM Foundations (2026-05-27 → 2026-06-03)

- [ ] Install Flutter SDK
- [ ] Create sample Flutter app
- [ ] Add audio recorder to Flutter (or native prototype)
- [ ] Study Android audio service lifecycle
- [ ] Study prompt engineering basics
- [ ] Build simple memory chat script
- [ ] **Checkpoint:** Basic Flutter app skeleton + understand LLM contexts

---

## Backlog

### Phase 1 — Desktop Prototype
- [ ] Design pipeline architecture
- [ ] Implement audio capture module
- [ ] Integrate Silero VAD
- [ ] Implement STT module
- [ ] Implement translation module
- [ ] Implement TTS module
- [ ] Build pipeline orchestrator
- [ ] Build desktop UI
- [ ] Latency logging
- [ ] Optimization and testing

### Phase 2 — Mobile MVP
- [ ] Set up Flutter + Kotlin project
- [ ] Android audio capture service
- [ ] Model conversion to mobile formats
- [ ] Bluetooth audio routing
- [ ] Offline mode verification
- [ ] Real-world testing

### Phase 3 — AI Reply Assistant
- [ ] Local LLM integration (llama.cpp)
- [ ] Prompt template system
- [ ] Context memory implementation
- [ ] Approval flow UI
- [ ] Mode system (meeting, travel, casual)
- [ ] Hallucination testing

### Phase 4 — Wearable Device
- [ ] Hardware platform research
- [ ] ESP32 firmware development
- [ ] BLE audio streaming
- [ ] Wearable integration with mobile app
- [ ] Battery optimization
- [ ] Prototype build and test

---

## Lessons Learned

<!-- Add entries here as you discover things. Format: Date — What happened — What to do differently. -->

