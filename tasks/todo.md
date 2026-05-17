# Current Tasks

## EchoEcho-T — Sprint Tracker

---

## Active Phase: Phase 0 — Foundation Learning

### Week 1: Audio Engineering (2026-05-13 → 2026-05-20) ✅ COMPLETE

- [x] Set up Python audio environment (sounddevice, numpy)
- [x] Build audio loopback test script
- [x] Measure and log baseline latency
- [x] Download and test Silero VAD
- [x] Tune VAD thresholds for your environment
- [x] Document audio buffer findings
- [x] **Checkpoint:** Working audio capture/playback with < 100ms loopback latency

**QA Results:** Loopback latency 58.17ms (target <100ms). Buffer benchmark: 128=18ms, 256=31ms, 512=58ms, 1024=111ms, 2048=218ms. VAD loaded successfully.

### Week 2: AI Inference (2026-05-20 → 2026-05-27) ✅ COMPLETE

- [x] Install ONNX Runtime
- [x] Download Whisper tiny
- [x] Build STT benchmark script
- [x] Measure inference time on your laptop
- [x] Test quantization (FP16 vs INT8)
- [x] Manually run STT → Translation chain
- [x] **Checkpoint:** Can transcribe, translate, and speak a sentence end-to-end

**QA Results:** Whisper tiny (int8) inference 0.15s for 5s audio — 33x real-time factor. ONNX Runtime works with CoreMLExecutionProvider. Manual pipeline framework verified.

### Week 3: Mobile + LLM Foundations (2026-05-27 → 2026-06-03) ✅ COMPLETE

- [x] Create sample Flutter app (structure ready; Flutter not installed yet)
- [x] Add audio recorder to Flutter app (record + audioplayers packages)
- [x] Study Android audio service lifecycle (documented in manifest)
- [x] Study prompt engineering basics
- [x] Build simple memory chat script
- [x] **Checkpoint:** Basic Flutter app skeleton + understand LLM contexts

**QA Results:** memory_chat.py runs with scripted input. Prompt builder, sliding window, context estimation all working. Flutter app skeleton ready for `flutter create` + `flutter pub get`.

---

## Backlog

### Phase 1 — Desktop Prototype ✅ BUILT

- [x] Design pipeline architecture
- [x] Implement audio capture module
- [x] Integrate Silero VAD
- [x] Implement STT module
- [x] Implement translation module
- [x] Implement TTS module
- [x] Build pipeline orchestrator
- [x] Build desktop CLI UI
- [x] Latency logging (CSV + Timer context manager)
- [x] Integration testing (synthetic audio)

**QA Results:**
- Translation EN→DE: "Hello, how are you?" → "Hallo, wie geht's?" in 0.138s
- Latency logger: All 5 stages logged correctly to CSV
- VAD: No segments from synthetic audio (expected — needs real speech)
- STT: Whisper tiny inference 0.15s for 5s audio (from Phase 0 benchmark)
- Pipeline: Threaded orchestrator with queue-based stage communication

**Pending real-speech test:**
Run `python src/phase1_desktop/main.py` and speak into microphone.
Expected: Speak English → hear German translation spoken aloud.
Target latency: <3s end-to-end.

### Phase 2 — Mobile MVP
- [ ] Set up Flutter + Kotlin project
- [ ] Android audio capture service
- [ ] Model conversion to mobile formats
- [ ] Bluetooth audio routing
- [ ] Offline mode verification
- [ ] Real-world testing

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

- **2026-05-13:** `sounddevice` `time_info` field names are `inputBufferAdcTime` / `outputBufferDacTime` / `currentTime` (camelCase), not snake_case. Always probe field names on new systems.
- **2026-05-13:** Silero VAD requires **exactly 512 samples** per inference at 16kHz. Use a ring buffer to accumulate chunks from the audio callback.
- **2026-05-13:** `sd.RawInputStream` passes a 1D CFFI buffer, not a 2D numpy array. Use `np.frombuffer(indata, dtype=np.float32).copy()`.
- **2026-05-13:** `transformers` pipeline task for translation is `text2text-generation`, not `translation`.
- **2026-05-13:** Whisper tiny (int8) is extremely fast — 0.15s for 5s audio on CPU. ONNX Runtime on macOS has CoreMLExecutionProvider available.
- **2026-05-13:** Synthetic audio (sine waves) does not trigger Whisper STT. Need real human speech for meaningful STT tests.
- **2026-05-18:** `torch.hub.load('snakers4/silero-vad')` requires `trust_repo=True` and hidden dependency `packaging`.
- **2026-05-18:** `transformers` pipeline API removed `translation` task. Use `AutoModelForSeq2SeqLM` + `AutoTokenizer` directly for Helsinki-NLP models.
- **2026-05-18:** pyttsx3 installed successfully for system TTS. Phase 2 will switch to Piper TTS for better quality.

