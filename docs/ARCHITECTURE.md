# System Architecture

## DamyDream — AI Communication Operating System

---

## Architectural Philosophy

1. **Latency-first:** Every design decision prioritizes reducing end-to-end latency
2. **Offline-first:** All core capabilities work without internet; cloud is optional enhancement
3. **Incremental complexity:** Add layers only when the foundation is solid
4. **Smartphone-as-hub:** Phone is the primary edge compute device; wearable is I/O peripheral
5. **Pipeline over orchestration:** Use simple streaming pipelines, not multi-agent systems

---

## MVP Architecture (Phase 1–2)

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Desktop   │  │   Mobile    │  │   Wearable (P4+)    │ │
│  │   (Py/Qt)   │  │  (Flutter)  │  │   (BLE Peripheral)  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  AUDIO CAPTURE  │
                    │  (Mic / BLE)    │
                    └────────┬────────┘
                             │ Audio Stream
                             ▼
                    ┌─────────────────┐
                    │  VAD (Silero)   │
                    │ Voice Detection │
                    └────────┬────────┘
                             │ Speech Segments
                             ▼
                    ┌─────────────────┐
                    │   STT (Whisper) │
                    │  Speech-to-Text │
                    └────────┬────────┘
                             │ Transcript
                             ▼
                    ┌─────────────────┐
                    │  TRANSLATION    │
                    │   (NLLB /       │
                    │  Argos Translate)│
                    └────────┬────────┘
                             │ Translated Text
                             ▼
                    ┌─────────────────┐
                    │   TTS (Piper)   │
                    │  Text-to-Speech │
                    └────────┬────────┘
                             │ Audio Stream
                             ▼
                    ┌─────────────────┐
                    │  AUDIO OUTPUT   │
                    │ (Speaker / BLE) │
                    └─────────────────┘
```

---

## Mobile Edge Architecture (Phase 2+)

```
┌─────────────────────────────────────────────────────────────┐
│                        ANDROID PHONE                          │
│                   (Primary Edge Compute)                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  FLUTTER APP SHELL                        ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  ││
│  │  │     UI      │  │   State     │  │   Audio Manager │  ││
│  │  │   Layer     │  │   Mgmt      │  │   (Routing)     │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              KOTLIN NATIVE MODULES                      ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  ││
│  │  │  Bluetooth  │  │   Audio     │  │  Background     │  ││
│  │  │    BLE      │  │   HAL       │  │   Service       │  ││
│  │  │  Manager    │  │ (AAudio)    │  │                 │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              AI RUNTIME ENGINE                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  ││
│  │  │ ONNX Runtime│  │  llama.cpp  │  │  TensorFlow Lite│  ││
│  │  │   Mobile    │  │   (LLM)     │  │    (Optional)   │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              AI PIPELINE ENGINE                         ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  ││
│  │  │    VAD      │  │    STT      │  │   Translation   │  ││
│  │  │  (Silero)   │  │  (Whisper)  │  │   (NLLB)        │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  ││
│  │  ┌─────────────┐  ┌─────────────┐                        ││
│  │  │    TTS      │  │   Context   │                        ││
│  │  │  (Piper)    │  │   Memory    │                        ││
│  │  └─────────────┘  └─────────────┘                        ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────┬──────────────────────────────────┘
                           │ BLE / Classic Bluetooth
┌──────────────────────────▼──────────────────────────────────┐
│                  BLUETOOTH EARBUDS                          │
│              (Audio I/O Peripheral)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Microphone Array → Audio Input                         ││
│  │  Speaker → Audio Output                               ││
│  │  BLE → Control / Status                               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Future Hybrid Architecture (Phase 4–5)

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   WEARABLE   │◄───────►│  SMARTPHONE  │◄───────►│ CLOUD AI     │
│   DEVICE     │   BLE   │  EDGE RUNTIME│  WiFi/5G│ (Optional)   │
│              │         │              │         │              │
│ • Mic array  │         │ • AI Pipeline│         │ • Heavy LLM  │
│ • Battery    │         │ • Local STT  │         │ • Vector DB  │
│ • Minimal UI │         │ • Edge LLM   │         │ • Sync       │
│ • BLE trans. │         │ • Audio I/O  │         │ • Analytics  │
└──────────────┘         └──────────────┘         └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  LLM REASON  │
                         │    LAYER     │
                         │              │
                         │ • Reply gen  │
                         │ • Context    │
                         │ • Memory     │
                         │ • Personality│
                         └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  PERSISTENCE │
                         │              │
                         │ • Conv. store│
                         │ • User prefs │
                         │ • Analytics  │
                         └──────────────┘
```

---

## Data Flow (Phase 2+)

```
1. Audio Capture
   └─→ Bluetooth earbuds OR phone mic
       └─→ Raw PCM stream (16kHz, 16-bit)

2. Voice Activity Detection
   └─→ Silero VAD processes chunks
       └─→ Speech detected? → Forward to STT
       └─→ Silence? → Buffer / Discard

3. Speech-to-Text
   └─→ Whisper (tiny/base) on ONNX Runtime
       └─→ Text transcript (source language)
       └─→ Confidence score

4. Translation
   └─→ NLLB (small) or Argos Translate
       └─→ Translated text (target language)
       └─→ Alternative translations (optional)

5. Context Analysis (Phase 3+)
   └─→ Conversation history
       └─→ AI reply suggestion
       └─→ User approval gate

6. Text-to-Speech
   └─→ Piper TTS (target voice)
       └─→ Synthesized audio stream

7. Audio Playback
   └─→ Phone speaker OR Bluetooth earbuds
```

---

## Technology Stack by Layer

### Audio Layer
| Component | Phase 1 | Phase 2+ | Notes |
|---|---|---|---|
| Capture | sounddevice (Python) | AAudio / Oboe (Kotlin) | 16kHz, 16-bit PCM |
| VAD | Silero VAD (ONNX) | Silero VAD Mobile | Aggressive for low latency |
| Playback | sounddevice | AAudio / Oboe | Low-latency audio track |
| Bluetooth | — | Android BluetoothProfile | Classic + BLE |

### AI Inference Layer
| Component | Phase 1 | Phase 2+ | Notes |
|---|---|---|---|
| Runtime | PyTorch / ONNX | ONNX Runtime Mobile | Quantized INT8 |
| STT | faster-whisper | Whisper ONNX / tiny | Streaming capable |
| Translation | transformers (NLLB) | NLLB ONNX / Argos | Lightweight models |
| TTS | piper-tts | Piper ONNX Mobile | Fast synthesis |
| LLM (P3+) | llama.cpp desktop | llama.cpp mobile | 2–4B params max |

### Application Layer
| Component | Phase 1 | Phase 2+ | Notes |
|---|---|---|---|
| UI | Tkinter / PyQt | Flutter | Cross-platform |
| State | In-memory | Hive / SQLite | Minimal, local-only |
| Config | JSON files | SharedPreferences | Per-mode settings |
| Background | Python threads | Android Services | Foreground service for audio |

---

## Model Zoo

### Phase 1–2 (Desktop + Mobile)

| Model | Purpose | Size | Format | Source |
|---|---|---|---|---|
| Whisper tiny | STT | 39M | ONNX / GGML | OpenAI / community |
| Whisper base | STT (better accuracy) | 74M | ONNX / GGML | OpenAI / community |
| NLLB-200-distilled-600M | Translation | 600M | ONNX | Meta |
| Piper TTS voices | TTS | ~20M each | ONNX | rhasspy/piper |
| Silero VAD | Voice detection | ~1M | ONNX | snakers4/silero |

### Phase 3+ (AI Assistant)

| Model | Purpose | Size | Format | Source |
|---|---|---|---|---|
| Phi-3-mini | Reply generation | 3.8B | GGUF / ONNX | Microsoft |
| Gemma-2B | Reply generation | 2B | GGUF / ONNX | Google |
| Qwen2-1.5B | Multilingual LLM | 1.5B | GGUF | Alibaba |
| All-MiniLM-L6-v2 | Embedding / memory | 22M | ONNX | sentence-transformers |

---

## Key Architectural Decisions

### 1. Pipeline vs. Agent Architecture
**Decision:** Simple streaming pipeline, not multi-agent orchestration.
**Rationale:** Multi-agent adds latency and complexity. A pipeline with configurable stages is sufficient for translation. Agents can be introduced later for advanced reasoning.

### 2. Phone as Hub vs. Wearable as Hub
**Decision:** Smartphone is the primary compute hub; wearable is audio I/O.
**Rationale:** Phone has battery, thermal headroom, and powerful NPUs. Wearable hardware is risky and expensive to prototype. This also enables faster iteration.

### 3. Offline-First vs. Cloud-First
**Decision:** All core inference runs on-device. Cloud is optional fallback.
**Rationale:** Privacy, latency, and cost. Network calls add 200ms–2s unpredictably. Offline-first ensures the product works everywhere.

### 4. Flutter + Kotlin vs. Native Android
**Decision:** Flutter for UI, Kotlin native modules for audio/Bluetooth.
**Rationale:** Flutter enables future iOS port with minimal work. Kotlin handles platform-specific audio APIs that Flutter cannot access directly.

### 5. Quantization Strategy
**Decision:** INT8 quantization for all models on mobile.
**Rationale:** 2–4x speedup, 2–4x memory reduction. Minimal accuracy loss for translation and TTS. STT may use FP16 if accuracy degrades on INT8.

---

## Latency Budget (Target: < 2s mobile)

| Stage | Budget | Technique |
|---|---|---|
| Audio capture + VAD | 100–300ms | Streaming chunks, aggressive VAD |
| STT (Whisper tiny) | 300–800ms | ONNX Runtime, quantization, streaming |
| Translation (NLLB) | 200–500ms | Small model, batched if possible |
| TTS (Piper) | 100–300ms | Fast voice, audio streaming |
| Audio playback | 50–100ms | Low-latency audio track |
| **Total** | **< 2s target** | **< 1s aspirational** |

---

## Scalability & Extensibility

### Adding New Languages
1. Add NLLB language pair
2. Add Piper voice model for target language
3. Update UI language selector
4. Test with native speaker

### Adding New Modes (Meeting, Travel)
1. Define mode-specific prompt templates (Phase 3+)
2. Configure context memory window size
3. Adjust VAD parameters (aggressive vs. lenient)
4. Add mode-specific UI chrome

### Cloud Fallback
1. Detect local inference failure (timeout, accuracy threshold)
2. Stream audio to cloud STT API (Deepgram, Whisper API)
3. Use cloud translation if local NLLB fails
4. Cache results locally for future offline use

---

## Security & Privacy

- All processing on-device by default
- No audio data leaves the device in offline mode
- Cloud mode requires explicit user opt-in per session
- No persistent storage of conversation audio (configurable)
- Transcript history encrypted at rest (Phase 3+)
- BLE connections use pairing / encryption

---

## Monitoring & Observability

### Phase 1–2
- Log latency per pipeline stage
- Log inference time per model
- Log audio buffer underruns/overruns
- Simple CSV / JSON log files

### Phase 3+
- In-app latency dashboard
- Crashlytics / Firebase (if cloud opt-in)
- Usage analytics (anonymized)
- Model accuracy feedback loop
