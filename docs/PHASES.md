# Detailed Phase Breakdown

## EchoEcho-T — Technical Specifications Per Phase

---

## Phase 0 — Foundation Learning

### Objective
Acquire the minimum viable knowledge to build real-time AI audio systems.

### Topics & Resources

#### Audio Engineering
| Topic | Resource | Time |
|---|---|---|
| Audio basics (sample rate, bit depth, buffers) | sounddevice docs | 2h |
| Streaming audio capture | sounddevice examples | 4h |
| Bluetooth audio on Android | Android developer docs | 4h |
| VAD concepts | Silero VAD README + paper | 4h |
| Latency measurement techniques | Loopback testing | 4h |

#### AI Inference
| Topic | Resource | Time |
|---|---|---|
| Whisper architecture | OpenAI Whisper paper | 4h |
| ONNX Runtime basics | ONNX Runtime docs | 4h |
| Quantization (INT8, FP16) | ONNX Runtime quantization guide | 4h |
| Edge AI concepts | Google Edge AI blog | 2h |
| Streaming inference patterns | faster-whisper README | 4h |

#### Mobile Development
| Topic | Resource | Time |
|---|---|---|
| Flutter setup + basics | Flutter codelabs | 8h |
| Android audio APIs | Android developer docs (AAudio) | 4h |
| Background services | Android foreground services guide | 4h |
| Bluetooth permissions | Android Bluetooth docs | 2h |

#### AI/LLM Concepts
| Topic | Resource | Time |
|---|---|---|
| Prompt engineering | OpenAI prompt engineering guide | 4h |
| Context windows | Claude / GPT docs | 2h |
| Conversational memory | LangChain memory docs (concepts only) | 2h |
| Streaming LLM output | llama.cpp server example | 4h |

### Deliverables
1. Audio loopback script with latency logging
2. Local Whisper inference benchmark script
3. Simple Flutter audio recorder app
4. Basic memory-enabled chat script (Python)

### Success Criteria
- Audio loopback latency < 100ms
- Whisper tiny inference < 2s per utterance
- Can explain VAD threshold tuning
- Flutter app runs on Android emulator or device

---

## Phase 1 — Desktop Prototype

### Objective
End-to-end proof of concept on laptop: speak in one language, hear translation in another.

### Technical Specification

#### Audio Capture Module
```python
# Requirements
- Library: sounddevice
- Sample rate: 16kHz (Whisper default)
- Bit depth: 16-bit PCM
- Buffer size: 512–1024 samples (32–64ms)
- Format: Streaming chunks, not file-based
```

#### VAD Module
```python
# Requirements
- Model: Silero VAD v4.0
- Format: ONNX
- Input: 16kHz, 16-bit PCM chunks
- Output: Speech probability (0.0–1.0)
- Trigger threshold: 0.5 (tune per environment)
- Padding: 300ms before/after speech
- Min speech duration: 250ms
```

#### STT Module
```python
# Requirements
- Model: Whisper tiny or base
- Backend: faster-whisper (CTranslate2) or ONNX
- Language: Auto-detect or manual select
- Output: Text transcript + confidence
- Target inference time: < 1s for 5s utterance
```

#### Translation Module
```python
# Requirements
- Model: NLLB-200-distilled-600M or Argos Translate
- Backend: transformers or ONNX
- Language pairs: EN↔TA, EN↔JA, EN↔ZH (minimum)
- Output: Translated text
- Target inference time: < 500ms
```

#### TTS Module
```python
# Requirements
- Model: Piper TTS
- Voices: One per target language
- Backend: ONNX Runtime
- Output: 22kHz PCM audio
- Target synthesis time: < 200ms per sentence
```

#### Pipeline Orchestrator
```python
# Requirements
- Architecture: Producer-consumer queues
- Audio capture → VAD → STT → Translation → TTS → Playback
- Each stage runs in separate thread
- Queue size: 2–3 items max (minimize buffering)
- Latency logging: Per-stage and end-to-end
```

#### UI Specification
```
- Start/Stop button
- Source language dropdown
- Target language dropdown
- Status indicator (idle, listening, processing, speaking)
- Latency display (live updating)
- Log viewer (optional)
```

### File Structure
```
src/phase1_desktop/
├── audio/
│   ├── capture.py      # Microphone input
│   ├── playback.py     # Speaker output
│   └── buffer.py       # Audio buffer management
├── ai/
│   ├── vad.py          # Silero VAD wrapper
│   ├── stt.py          # Whisper STT wrapper
│   ├── translate.py    # NLLB translation wrapper
│   └── tts.py          # Piper TTS wrapper
├── pipeline/
│   ├── queue.py        # Inter-stage queues
│   ├── worker.py       # Stage worker threads
│   └── orchestrator.py # Main pipeline controller
├── ui/
│   └── main.py         # Desktop UI (Tkinter or PyQt)
├── config/
│   └── settings.yaml   # Model paths, thresholds, languages
├── utils/
│   ├── latency.py      # Latency logging
│   └── logger.py       # Application logging
├── main.py             # Entry point
└── requirements.txt
```

### Testing Plan
1. **Lab test:** Quiet room, 10 utterances per language pair
2. **Noise test:** Cafe or street environment, 5 utterances
3. **Latency test:** Log every stage, calculate p50/p95/p99
4. **Stress test:** Continuous conversation for 5 minutes

### Deliverables
1. Working desktop application
2. Latency benchmark report (CSV/JSON)
3. README with setup instructions
4. Tag: `phase-1-complete`

---

## Phase 2 — Mobile MVP

### Objective
Port working pipeline to Android. Primary interaction: Bluetooth earbuds.

### Technical Specification

#### Flutter App Shell
```dart
// Requirements
- Framework: Flutter 3.19+
- State management: Riverpod or Bloc
- Audio: ffi to Kotlin native modules
- UI: Material Design 3
- Platforms: Android (iOS future)
```

#### Kotlin Native Modules
```kotlin
// Requirements
- Audio capture: AAudio API (low latency)
- Audio playback: AAudio API
- Bluetooth: Android BluetoothProfile (Classic + BLE)
- Background: ForegroundService with persistent notification
- Threading: Coroutines for audio I/O
```

#### AI Runtime (Android)
```
- ONNX Runtime Mobile 1.17+
- llama.cpp (optional, for Phase 3)
- TensorFlow Lite (optional fallback)
- All models: INT8 quantized
- Model storage: App private directory
- Lazy loading: Load model on first use
```

#### Pipeline (Mobile)
```
- Same stages as Phase 1
- Audio I/O via Kotlin native modules
- AI inference via ONNX Runtime Mobile (C++ or Java API)
- Flutter UI displays status and latency
- Push-to-talk: Physical button or UI button
- Conversation mode: Auto-detect speaker turns via VAD
```

#### Bluetooth Integration
```
- Profile: A2DP (audio) + HFP (mic) + BLE (control)
- Audio routing: Force audio to Bluetooth when connected
- Fallback: Phone speaker/mic if Bluetooth disconnected
- Tested devices: Minimum 2 brands
```

#### Offline Requirements
```
- All models bundled in APK or downloaded on first run
- No network calls in core pipeline
- Optional: Cloud fallback with user opt-in
- Airplane mode test: Must pass
```

### File Structure
```
src/phase2_mobile/
├── android/
│   ├── app/
│   │   └── src/main/kotlin/com/echoecho-t/
│   │       ├── audio/
│   │       │   ├── AudioCaptureService.kt
│   │       │   ├── AudioPlaybackManager.kt
│   │       │   └── AudioBuffer.kt
│   │       ├── bluetooth/
│   │       │   ├── BluetoothManager.kt
│   │       │   └── BluetoothAudioRouter.kt
│   │       └── pipeline/
│   │           ├── PipelineService.kt
│   │           └── NativeBridge.kt
│   └── build.gradle
├── lib/
│   ├── main.dart
│   ├── screens/
│   │   ├── home_screen.dart
│   │   └── settings_screen.dart
│   ├── widgets/
│   │   ├── language_selector.dart
│   │   ├── status_indicator.dart
│   │   └── latency_display.dart
│   ├── providers/
│   │   └── pipeline_state.dart
│   └── services/
│       └── native_channel.dart
├── assets/
│   ├── models/           # ONNX models (git-lfs or download script)
│   └── voices/           # Piper voice models
├── pubspec.yaml
└── README.md
```

### Testing Plan
1. **Device test:** Samsung S24 or equivalent, 20 utterances
2. **Bluetooth test:** Sony + Nothing earbuds, 10 utterances each
3. **Offline test:** Airplane mode, 10 utterances
4. **Field test:** 5 real conversations with humans
5. **Battery test:** 30 minutes continuous use, measure drain

### Deliverables
1. Android APK that installs and runs independently
2. Offline capability verified
3. Bluetooth audio I/O working with 2+ earbud models
4. User feedback from 5+ real conversations
5. Latency report (mobile benchmarks)
6. Tag: `phase-2-complete`

---

## Phase 3 — AI Reply Assistant

### Objective
Add conversational intelligence: AI suggests replies, user approves, AI speaks.

### Technical Specification

#### LLM Integration
```
- Primary: Phi-3-mini-4k-instruct (GGUF, 3.8B)
- Fallback: Gemma-2B-it or Qwen2-1.5B-Instruct
- Backend: llama.cpp (mobile-optimized build)
- Quantization: Q4_K_M (balance of speed/quality)
- Context window: 4K tokens
- Target inference: < 2s for reply generation
```

#### Prompt Engineering
```
System prompt template:
"You are a helpful conversation assistant. The user is having a conversation in [target_language]. Based on the context, suggest a natural, culturally appropriate reply. Keep it brief (1–2 sentences)."

User prompt includes:
- Conversation history (last 6 turns)
- Current utterance (translated)
- Mode context (meeting, travel, casual)
- Target language
```

#### Context Memory
```
- Storage: SQLite or Hive (local)
- Format: Conversation turns (speaker, text, timestamp, language)
- Retention: Last 50 turns or 30 minutes
- Summarization: Optional, if context > 4K tokens
- Privacy: No cloud sync by default
```

#### Approval Flow
```
1. AI generates 1–3 reply suggestions
2. Display as cards in UI
3. User taps to approve + speak
4. User swipes to reject → AI regenerates
5. Optional: "Always use first suggestion" setting (power user)
```

#### Modes
```
- Casual: Friendly, informal tone
- Meeting: Professional, concise
- Travel: Common phrases, directions, numbers
- Custom: User-defined prompt template
```

### File Structure
```
src/phase3_ai_reply/
├── llm/
│   ├── inference.py            # Desktop wrapper
│   ├── inference_mobile.cpp    # llama.cpp mobile bridge
│   ├── prompt_builder.py       # Prompt template engine
│   └── context_manager.py      # Conversation memory
├── ui/
│   ├── reply_suggestion.dart   # Suggestion cards
│   ├── approval_flow.dart      # Approve/reject UI
│   └── mode_selector.dart      # Mode picker
├── modes/
│   ├── casual.yaml
│   ├── meeting.yaml
│   ├── travel.yaml
│   └── custom.yaml
├── memory/
│   ├── conversation_store.dart
│   └── summarizer.dart
└── tests/
    ├── hallucination_test.py
    └── relevance_test.py
```

### Testing Plan
1. **Accuracy test:** 50 conversations, measure hallucination rate
2. **Relevance test:** AI replies rated 1–5 by tester
3. **Latency test:** Reply generation + approval + TTS < 3s
4. **UX test:** 10 non-technical users try approval flow

### Deliverables
1. AI reply generation working locally
2. Approval flow UI in Flutter
3. Hallucination rate < 5% (documented)
4. Context memory persisting across sessions
5. Tag: `phase-3-complete`

---

## Phase 4 — Wearable Device

### Objective
Move from phone-centric to wearable + phone hybrid.

### Technical Specification

#### Hardware Platform Options

| Platform | Pros | Cons | Cost |
|---|---|---|---|
| ESP32-S3 | Cheap, BLE, low power | Weak AI, needs phone for inference | $5–10 |
| Raspberry Pi Zero 2W | Linux, easy dev | Power hungry, bulky | $15–20 |
| Qualcomm QCS2290 | AI acceleration | Expensive, complex | $50–100 |
| Custom ARM (nRF5340) | Purpose-built | Requires EE expertise | $10–20 + design |

**Recommended:** ESP32-S3 for audio I/O + BLE, phone for inference.

#### Wearable Specifications
```
Form factor: Clip-on or pendant (30–40mm diameter)
Microphone: MEMS mic (Knowles SPH0645 or similar)
Audio: 16kHz, 16-bit PCM streaming
Connectivity: BLE 5.0 (audio + control)
Battery: 200mAh Li-Po (target 4h+)
Charging: USB-C or wireless Qi
Indicators: 2x RGB LED (status), haptic motor
Controls: 1x capacitive touch or physical button
```

#### Firmware (ESP32-S3)
```
- Framework: ESP-IDF or Arduino
- Audio: I2S microphone, 16kHz
- BLE: GATT server (audio stream characteristic)
- Power: Deep sleep between utterances, wake-on-VAD
- OTA: Firmware update capability
```

#### Phone Integration Changes
```
- Add BLE peripheral audio source
- Modify pipeline: BLE audio → VAD → STT → ... → TTS → Bluetooth earbuds
- Wearable status in UI (battery, connection quality)
- Wearable configuration (LED brightness, haptic intensity)
```

### File Structure
```
src/phase4_wearable/
├── firmware/
│   ├── esp32/
│   │   ├── main/
│   │   │   ├── audio_task.c
│   │   │   ├── ble_gatt.c
│   │   │   ├── power_manager.c
│   │   │   └── main.c
│   │   └── CMakeLists.txt
│   └── README.md
├── hardware/
│   ├── schematics/
│   ├── pcb/
│   └── enclosure/
│       └── case.step
├── mobile_updates/
│   └── ble_audio_source.dart
└── tests/
    ├── battery_life.py
    ├── audio_quality.py
    └── range_test.py
```

### Testing Plan
1. **Audio quality:** Wearable mic vs. phone mic, MOS score
2. **Battery life:** Continuous use until shutdown
3. **Range test:** BLE connection stability at 2m, 5m, 10m
4. **Durability:** Drop test, sweat exposure (IPX4 target)

### Deliverables
1. Working wearable prototype (at least 1 unit)
2. BLE audio streaming to phone
3. Battery life > 4 hours
4. Audio quality comparable to phone mic
5. Cost estimate for 100-unit manufacturing
6. Tag: `phase-4-complete`

---

## Phase 5 — Autonomous Conversational Agent (Future)

**Not detailed here.** Will be scoped after Phase 4 completion based on:
- Wearable adoption and feedback
- Edge AI hardware improvements
- Local LLM capability advances

Potential scope:
- Autonomous reply mode with trust levels
- Persistent memory across days/weeks
- Emotional tone matching
- Speaker identification
- Smart interruption handling
