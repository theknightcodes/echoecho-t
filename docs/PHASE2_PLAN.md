# Phase 2 — Mobile MVP Plan

## EchoEcho-T: Real-Time Translation on Android

**Date:** 2026-05-23  
**Status:** Draft  
**Owner:** Engineering Lead  
**Target:** Working Android APK with offline pipeline (VAD → STT → Translation → TTS)

---

## 1. Architecture Decision Record (ADR)

### ADR-001: Flutter + Kotlin Native Modules vs. Pure Kotlin Native

**Context:** Phase 1 proved the pipeline on desktop (Python). Phase 2 must port it to Android with primary interaction through Bluetooth earbuds. We need a UI framework and a way to access low-level audio/Bluetooth APIs.

**Options Considered:**

| Criteria | Flutter + Kotlin | Pure Kotlin Native | React Native + JSI | Compose Multiplatform |
|---|---|---|---|---|
| **Dev Speed** | Fast UI iteration; one codebase for Android + future iOS | Slower; must rewrite for iOS later | Medium; JS bridge latency for audio | Fast UI; but native interop still needed |
| **Audio Latency** | Excellent (audio runs in Kotlin native modules, not Dart) | Excellent (direct AAudio/Oboe) | Poor (JSI bridge adds 5–20ms) | Good (still needs native interop) |
| **Performance** | Native-speed audio/AI; Flutter UI is 60fps | Native-speed everywhere | Audio streaming is risky | Native-speed audio/AI |
| **Team Skill Fit** | Dart (new) + Kotlin (familiar) | Kotlin only | JavaScript (familiar) + C++ | Kotlin (familiar) |
| **iOS Portability** | Reuse 90%+ UI code; rewrite only native modules | Full rewrite required | Reuse 80% JS code | Reuse 80% UI code |
| **Ecosystem** | Rich plugin ecosystem; ONNX Runtime Mobile bindings exist | Full Android ecosystem | Audio plugins are immature | Young ecosystem; fewer audio libs |
| **Background Audio** | Kotlin ForegroundService + Flutter isolate; proven pattern | Standard Android Service | Complex; requires native modules anyway | Same as Flutter |
| **Build Complexity** | Two build systems (Gradle + Flutter) | Single Gradle build | Metro + Gradle + CMake | Gradle + Kotlin |

**Decision:** Flutter for UI + Kotlin native modules for audio, Bluetooth, and AI inference orchestration.

**Justification:**
1. **iOS future-proofing:** The long-term roadmap includes iOS. Flutter minimizes that future port. Pure Kotlin would force a complete UI rewrite.
2. **Latency is contained:** Audio capture, VAD, and playback run entirely in Kotlin native modules with zero Dart involvement in the hot path. Flutter only displays status and receives latency metrics via PlatformChannel (async, non-blocking).
3. **Proven pattern:** ONNX Runtime Mobile has official Flutter plugins and Kotlin/Java APIs. The bridge is well-documented.
4. **Team velocity:** UI iteration in Flutter is significantly faster than native Android, and the audio-critical code is still Kotlin where expertise matters.
5. **Risk mitigation:** If Flutter becomes a bottleneck, we can replace the UI layer later without touching the audio/AI pipeline because the Kotlin modules are cleanly separated.

**Trade-off accepted:** Slightly more complex build (two build systems) and a small communication latency between UI and engine (~1–5ms over PlatformChannel, negligible for status updates).

---

## 2. Technical Stack

### 2.1 Framework & SDK

| Layer | Technology | Version | Notes |
|---|---|---|---|
| UI Framework | Flutter | 3.27+ (stable) | Material Design 3, Impeller renderer on Android |
| Dart SDK | Dart | 3.6+ | Records, patterns, `dart:ffi` for future C++ direct calls |
| Android Language | Kotlin | 2.0+ | Coroutines, Flows, K2 compiler |
| Android SDK | API 28–35 | compileSdk 35, minSdk 28 | Android 9+ (covers 95%+ devices) |
| Android NDK | NDK | 27b+ | For Oboe C++ audio library and future C++ model bridges |
| JVM Target | Java 17 |  |  |

### 2.2 Audio Libraries

| Component | Library | Version | Justification |
|---|---|---|---|
| **Capture (Native)** | Oboe (C++) + Kotlin wrapper | 1.9+ | Lowest latency on Android; AAudio backend with OpenSLES fallback; 16kHz, 16-bit PCM |
| **Playback (Native)** | Oboe (C++) + Kotlin wrapper | 1.9+ | Same reason; supports low-latency audio streams |
| **Flutter Bridge** | `pigeon` (Google) | latest | Type-safe, fast PlatformChannel code generation between Dart and Kotlin |
| **Alternative fallback** | `flutter_sound` | 9.x | If Oboe integration proves too time-consuming, use for rapid prototyping only |

**Rationale for Oboe over AudioRecord/AudioTrack:**
- AudioRecord/AudioTrack are Java APIs with higher latency and less control over buffer sizes.
- Oboe is a C++ wrapper over AAudio (Android 8.1+) with automatic OpenSLES fallback.
- Oboe provides a shared-memory audio stream that avoids JNI copies, saving ~5–10ms.

### 2.3 AI Runtime & Model Conversion

| Component | Technology | Version | Notes |
|---|---|---|---|
| Primary Runtime | ONNX Runtime Mobile | 1.20+ | Official Android Java/Kotlin bindings; `onnxruntime-android` AAR |
| Alternative Runtime | TensorFlow Lite | 2.18+ | Fallback if ONNX model performance is poor on specific ops |
| Whisper Runtime | whisper.cpp (Kotlin JNI) | latest | Faster than ONNX for Whisper; GGML/GGUF quantization; community Kotlin bindings exist |
| Model Storage | App private directory | — | `getFilesDir()/models/`; lazy load on first use |
| Quantization | INT8 (static/dynamic) | — | ONNX Runtime quantization tools; whisper.cpp Q5_0/Q8_0 |

**Model Conversion Pipeline:**

```
PyTorch (.pt/.bin)
    ↓  torch.onnx.export()  OR  transformers.onnx
ONNX (.onnx)
    ↓  onnxruntime.quantization (INT8, dynamic)
ONNX Quantized (.onnx, ~50% size)
    ↓  onnxruntime-mobile optimization
Mobile-Optimized ONNX (.ort)
    ↓  bundled in APK or downloaded on first run
Device Storage
```

**Whisper Mobile Options Decision:**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **whisper.cpp (GGML)** | Fastest on CPU; excellent community; tiny model runs in <300ms on flagship | Requires JNI/C++ bridge; Kotlin bindings need maintenance | **Primary choice** |
| **ONNX Runtime (Whisper tiny ONNX)** | Unified runtime with other models; easy Java/Kotlin API | Slower than whisper.cpp; streaming support is patchy | **Backup / unified runtime** |
| **Cloud API (Deepgram, OpenAI)** | Best accuracy; no model size concern | Violates offline-first mandate; adds 200ms–2s latency; ongoing cost | **Opt-in fallback only** |

**Decision:** Use whisper.cpp as the primary STT runtime. The performance gain over ONNX is significant enough to justify a second runtime in the app. All other models (VAD, translation, TTS) run on ONNX Runtime Mobile for runtime uniformity.

### 2.4 NLLB Mobile Feasibility

**Model:** NLLB-200-distilled-600M  
**Original Size (FP32):** ~2.4 GB  
**FP16 Size:** ~1.2 GB  
**INT8 Size:** ~600 MB  
**INT4 (GPTQ/AWQ equivalent via ONNX):** ~300–350 MB (accuracy TBD)

| Quantization | Size | Latency (est.) | Quality | Feasibility |
|---|---|---|---|---|
| FP32 | 2.4 GB | — | Best | Impossible (APK size limit, OOM) |
| FP16 | 1.2 GB | 800ms–1.5s | Excellent | Marginal (still large) |
| **INT8** | **~600 MB** | **400–800ms** | **Good** | **Viable** |
| INT4 (experimental) | ~300 MB | 300–600ms | Moderate | Research task |

**Decision:** Target INT8 quantization for NLLB. If INT8 quality is unacceptable for certain language pairs, evaluate Argos Translate (smaller, lower quality) as a fallback for those languages only.

**Mitigation for model size:**
- Do not bundle NLLB in the APK. Download on first run via a background download manager.
- Split by language pair: only download the encoder/decoder matrices for the active language pair if feasible (ONNX Runtime supports model partitioning).
- Use `split_seq2seq_to_onnx.py` from transformers to export encoder and decoder separately, enabling decoder caching.

### 2.5 TTS

| Component | Technology | Size | Notes |
|---|---|---|---|
| Runtime | ONNX Runtime Mobile | — | Piper voices are ONNX natively |
| Model | Piper TTS voices | ~20–50 MB per language | 22kHz PCM output; fast synthesis |
| Voices | One per target language | — | EN, TA, JA, ZH as Phase 2 priorities |

---

## 3. Project Structure

```
/Users/dhamotharanpalanisamy/projects/echoecho-t/
├── src/
│   └── phase2_mobile/
│       ├── android/
│       │   ├── app/
│       │   │   ├── build.gradle.kts
│       │   │   └── src/
│       │   │       └── main/
│       │   │           ├── AndroidManifest.xml
│       │   │           ├── cpp/                          # NDK / Oboe / whisper.cpp JNI
│       │   │           │   ├── CMakeLists.txt
│       │   │           │   ├── oboe_audio.cpp             # Oboe capture + playback
│       │   │           │   ├── whisper_jni.cpp            # JNI bridge to whisper.cpp
│       │   │           │   └── native-lib.cpp             # General native utilities
│       │   │           ├── kotlin/
│       │   │           │   └── com/echoecho/
│       │   │               ├── EchoEchoApplication.kt
│       │   │               ├── audio/
│       │   │               │   ├── AudioCaptureManager.kt     # Kotlin wrapper over Oboe
│       │   │               │   ├── AudioPlaybackManager.kt      # Kotlin wrapper over Oboe
│       │   │               │   ├── AudioBuffer.kt               # Ring buffer for PCM
│       │   │               │   └── AudioRouter.kt             # Mic vs Bluetooth routing
│       │   │               ├── bluetooth/
│       │   │               │   ├── BluetoothManager.kt          # Discovery, pairing
│       │   │               │   ├── BluetoothAudioRouter.kt      # A2DP + HFP routing
│       │   │               │   └── BluetoothProfileListener.kt  # Connection state
│       │   │               ├── pipeline/
│       │   │               │   ├── PipelineService.kt           # ForegroundService
│       │   │               │   ├── PipelineOrchestrator.kt      # Stage controller
│       │   │               │   ├── NativeBridge.kt              # FFI / JNI coordinator
│       │   │               │   └── ModelManager.kt              # Load/unload ONNX models
│       │   │               ├── ai/
│       │   │               │   ├── WhisperEngine.kt               # whisper.cpp wrapper
│       │   │               │   ├── NllbTranslator.kt            # ONNX Runtime NLLB wrapper
│       │   │               │   ├── VadEngine.kt                 # Silero VAD ONNX wrapper
│       │   │               │   ├── TtsEngine.kt                   # Piper ONNX wrapper
│       │   │               │   └── LatencyLogger.kt             # Per-stage timing
│       │   │               └── platform/
│       │   │                   ├── PlatformChannel.kt           # Pigeon-generated bridge
│       │   │                   └── MainActivity.kt
│       │   └── build.gradle.kts
│       ├── lib/                    # Flutter Dart code
│       │   ├── main.dart
│       │   ├── app.dart
│       │   ├── screens/
│       │   │   ├── home_screen.dart
│       │   │   ├── settings_screen.dart
│       │   │   ├── onboarding_screen.dart      # Permissions + model download
│       │   │   └── language_pair_screen.dart
│       │   ├── widgets/
│       │   │   ├── status_indicator.dart       # Idle/Listening/Processing/Speaking
│       │   │   ├── latency_display.dart        # Live p50/p95/p99
│       │   │   ├── language_selector.dart      # Source + target dropdowns
│       │   │   └── bluetooth_device_picker.dart
│       │   ├── providers/
│       │   │   ├── pipeline_state_notifier.dart
│       │   │   ├── settings_provider.dart
│       │   │   └── bluetooth_provider.dart
│       │   ├── services/
│       │   │   └── native_channel_service.dart  # Dart side of Pigeon bridge
│       │   ├── models/
│       │   │   ├── pipeline_status.dart
│       │   │   ├── latency_metrics.dart
│       │   │   └── language_config.dart
│       │   └── theme/
│       │       └── app_theme.dart
│       ├── assets/
│       │   ├── models/
│       │   │   └── .gitkeep                   # Models downloaded at runtime
│       │   └── voices/
│       │       └── .gitkeep
│       ├── pigeon/
│       │   └── echoecho_api.dart              # Pigeon IDL definition
│       ├── test/
│       │   └── widget_test.dart
│       ├── pubspec.yaml
│       └── README.md
├── models/
│   └── mobile/                    # Conversion scripts + model configs
│       ├── convert_whisper_to_onnx.py
│       ├── convert_nllb_to_onnx.py
│       ├── quantize_int8.py
│       └── download_models.sh
├── docs/
│   └── PHASE2_PLAN.md             # This file
└── tasks/
    └── phase2_todo.md             # Living task list for Phase 2
```

### Module Separation

| Module | Responsibility | Language | Reason |
|---|---|---|---|
| **UI** | Screens, widgets, theming, state management | Dart (Flutter) | Fast iteration; cross-platform future |
| **Platform Bridge** | Type-safe Dart ↔ Kotlin communication | Dart + Kotlin (Pigeon) | Avoids manual MethodChannel boilerplate |
| **Audio HAL** | Capture, playback, buffer management, routing | Kotlin + C++ (Oboe) | Lowest latency; Bluetooth routing |
| **Bluetooth** | Pairing, connection state, audio routing | Kotlin | Android-specific APIs |
| **AI Engine** | Model loading, inference, quantization | Kotlin + C++ (JNI) | ONNX Java API; whisper.cpp JNI |
| **Pipeline** | Stage orchestration, queue management, latency logging | Kotlin | Coroutines + Flow for streaming |
| **Background Service** | Foreground service, notification, lifecycle | Kotlin | Android platform requirement |

---

## 4. Milestones

### Milestone 1: Flutter App Skeleton with Audio Permissions
**Target:** Week 1  
**Definition of Done:**
- [ ] Flutter project initialized at `src/phase2_mobile/`
- [ ] AndroidManifest.xml includes `RECORD_AUDIO`, `BLUETOOTH`, `BLUETOOTH_CONNECT`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_MICROPHONE` permissions
- [ ] Runtime permission flow implemented (Android 6+ dynamic permissions)
- [ ] Basic navigation scaffold: Home, Settings, Onboarding
- [ ] State management (Riverpod) wired up with placeholder providers
- [ ] Pigeon platform channel defined and generated (Dart ↔ Kotlin stub)
- [ ] App builds and runs on Android emulator (API 34) and physical device (Samsung S24 or equivalent)
- [ ] CI: `flutter build apk --release` passes in GitHub Actions

**Key Output:** Installable APK with working UI shell and permission flows.

---

### Milestone 2: Native Android Audio Capture Service
**Target:** Week 2–3  
**Definition of Done:**
- [ ] Oboe integrated via CMake/NDK; captures 16kHz 16-bit PCM mono
- [ ] Kotlin `AudioCaptureManager` exposes `startCapture()`, `stopCapture()`, `getStream(): Flow<ByteArray>`
- [ ] Kotlin `AudioPlaybackManager` exposes `playAudio(pcmData: ByteArray)`, `stopPlayback()`
- [ ] Ring buffer (`AudioBuffer.kt`) handles producer-consumer between capture and pipeline without allocation in hot path
- [ ] `PipelineService.kt` runs as Android ForegroundService with persistent notification
- [ ] Service survives screen lock and app backgrounding for at least 5 minutes
- [ ] Audio capture → playback loopback test passes with <50ms measured latency (using loopback cable or OboeTester methodology)
- [ ] Flutter UI displays live audio level meter from native stream

**Key Output:** Low-latency audio I/O running continuously in a foreground service, verified by loopback test.

---

### Milestone 3: Whisper STT Integration (On-Device)
**Target:** Week 4–5  
**Definition of Done:**
- [ ] whisper.cpp compiled for Android (arm64-v8a, armeabi-v7a) via CMake
- [ ] JNI bridge (`whisper_jni.cpp`) exposes `init(modelPath)`, `transcribe(pcmData, sampleRate)`, `free()`
- [ ] Kotlin `WhisperEngine` wraps JNI with coroutine-friendly `suspend fun transcribe(audio: FloatArray): String`
- [ ] Whisper tiny model (GGML Q8_0 or Q5_0) downloaded to device on first run
- [ ] VAD (Silero ONNX) segments audio stream; utterances forwarded to Whisper
- [ ] End-to-end test: Speak 10 English utterances into device → text appears in Flutter UI
- [ ] Inference time logged: p50 < 500ms for 5-second utterances on Samsung S24
- [ ] Language auto-detection works for EN, TA, JA, ZH
- [ ] Graceful degradation: if whisper.cpp fails to load, show error in UI and offer cloud fallback toggle

**Key Output:** Real-time speech-to-text working offline with <500ms p50 latency.

---

### Milestone 4: NLLB Translation Integration
**Target:** Week 6–7  
**Definition of Done:**
- [ ] NLLB-200-distilled-600M converted to ONNX (encoder + decoder)
- [ ] INT8 quantization applied; final model size < 650 MB per language direction
- [ ] ONNX Runtime Mobile loads NLLB without OOM on 8GB RAM devices
- [ ] Kotlin `NllbTranslator` wraps ONNX Runtime with beam search decoding (beam width = 2)
- [ ] Translation test: 50 sentence pairs per language direction (EN↔TA, EN↔JA, EN↔ZH)
- [ ] BLEU score within 5% of FP32 baseline (measured against desktop reference)
- [ ] Inference time logged: p50 < 800ms per sentence on Samsung S24
- [ ] Flutter UI displays translated text alongside source transcript
- [ ] If NLLB INT8 is too slow or large, Argos Translate fallback evaluated and documented

**Key Output:** Offline neural translation integrated, quality validated, size manageable.

---

### Milestone 5: TTS Integration
**Target:** Week 8  
**Definition of Done:**
- [ ] Piper voice models (ONNX) for EN, TA, JA, ZH downloaded to device
- [ ] Kotlin `TtsEngine` wraps ONNX Runtime Piper inference
- [ ] Synthesized audio is 22kHz PCM; resampled to 16kHz for Oboe playback if needed
- [ ] End-to-end test: Text input → synthesized speech heard through device speaker in < 300ms p50
- [ ] Voice selection per target language in Flutter Settings
- [ ] Audio ducking: TTS playback lowers volume if microphone is simultaneously active (prevents feedback)
- [ ] Queue-based TTS: multiple sentences queued and spoken sequentially without gaps

**Key Output:** Natural-sounding offline TTS for all target languages.

---

### Milestone 6: Full Pipeline Wiring
**Target:** Week 9  
**Definition of Done:**
- [ ] `PipelineOrchestrator` connects all stages: Audio → VAD → STT → Translation → TTS → Audio
- [ ] Each stage runs in a dedicated coroutine with a `Channel` of max size 1 (streaming, no batching)
- [ ] Latency logged per stage and end-to-end; displayed in Flutter UI in real time
- [ ] Push-to-talk mode: UI button or volume button long-press triggers capture
- [ ] Conversation mode: VAD auto-detects speaker turns; no button required
- [ ] Error handling: any stage failure surfaces a user-friendly message and pauses pipeline
- [ ] End-to-end latency test: 20 utterances, p50 < 2s target, p95 < 3s
- [ ] Stress test: 5-minute continuous conversation without crashes or memory leaks (verify via Android Studio Profiler)

**Key Output:** Complete offline translation pipeline with real-time metrics and two interaction modes.

---

### Milestone 7: Offline Mode Verification
**Target:** Week 10  
**Definition of Done:**
- [ ] All models (Whisper, NLLB, Piper, Silero VAD) present in app private directory
- [ ] Airplane mode test: 10 utterances per language pair, 100% success rate
- [ ] No network calls triggered during pipeline execution (verified via Android Studio Network Profiler)
- [ ] Cloud fallback toggle exists in Settings but is OFF by default
- [ ] If user opts into cloud fallback, explicit warning dialog shown about privacy
- [ ] First-run download manager handles model downloads with resume capability and storage checks
- [ ] APK size without models < 50 MB; with models (if bundled) < 100 MB (prefer download strategy)

**Key Output:** Verified offline-first operation; no accidental network dependencies.

---

### Milestone 8: Real-World Testing
**Target:** Week 11–12  
**Definition of Done:**
- [ ] Device test: Samsung S24 (or equivalent), 20 utterances per language pair
- [ ] Bluetooth test: Sony WH-1000XM5 + Nothing Ear (2) earbuds, 10 utterances each
- [ ] Audio routing verified: mic input from Bluetooth, playback to Bluetooth
- [ ] Noise test: Cafe environment (60–70 dB), 10 utterances, accuracy within 10% of quiet room
- [ ] Battery test: 30 minutes continuous conversation mode; measure battery drain and thermal throttling
- [ ] 5 real conversations with native speakers; collect qualitative feedback
- [ ] Latency report exported (CSV/JSON) with p50/p95/p99 per stage
- [ ] Bug fixes and performance tuning based on feedback
- [ ] Tag `phase-2-complete` pushed to repository

**Key Output:** Validated mobile MVP ready for limited user testing.

---

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **NLLB model too large for mobile (600M–1.2GB)** | High | Critical | Download on first run (not APK); split encoder/decoder; evaluate INT4 quantization; Argos Translate fallback; consider cloud fallback for low-end devices |
| **Battery consumption too high (AI + audio + Bluetooth)** | High | High | Aggressive VAD to avoid unnecessary STT/translation; model quantization reduces compute; foreground service with wake-lock management; benchmark and set user expectations |
| **Audio latency on Android (buffer underruns, Bluetooth delay)** | Medium | High | Oboe for low-latency paths; configurable buffer sizes; AAudio over OpenSLES when available; Bluetooth Classic (HFP) for mic has inherent ~100ms delay—document this |
| **Background execution limits (Android 12+)** | Medium | Medium | ForegroundService with `foregroundServiceType="microphone"`; persistent notification; test on Android 14/15; handle app-kill gracefully with save/restore state |
| **Bluetooth audio routing complexity (A2DP vs HFP)** | High | High | Explicit audio routing code in `BluetoothAudioRouter.kt`; force HFP for mic input when earbuds connected; fallback to phone mic if HFP unavailable; test 2+ earbud brands minimum |
| **whisper.cpp JNI build complexity** | Medium | Medium | Use community Kotlin bindings (e.g., `whispercpp` packages) if available; pin a stable whisper.cpp commit; CI build for Android ABIs |
| **Thermal throttling on long sessions** | Medium | Medium | 5-minute stress test early; if throttling occurs, reduce beam width, switch to smaller Whisper model dynamically, or alert user |
| **Model download failures on first run** | Medium | Medium | Resume-capable downloader; checksum verification; WiFi-only download with user consent; clear progress UI; offline error state if download fails |
| **iOS port delayed if Flutter native modules are Android-only** | Low | Medium | Design Kotlin modules behind a `PlatformChannel` interface; iOS port will need Swift/Objective-C equivalents but Flutter UI is 90% reusable |
| **NLLB INT8 quality degradation for low-resource languages** | Medium | Medium | Quantization-aware fine-tuning if needed; per-language quality gate; Argos Translate fallback for languages where NLLB INT8 fails |

---

## 6. First Steps (Start Today)

To begin Milestone 1 immediately:

1. **Install Flutter 3.27+ and Android SDK:**
   ```bash
   flutter doctor
   # Ensure Android toolchain, Android SDK, and NDK are fully installed.
   ```

2. **Create the Flutter project:**
   ```bash
   cd /Users/dhamotharanpalanisamy/projects/echoecho-t/src/
   flutter create --org com.echoecho --project-name phase2_mobile phase2_mobile
   cd phase2_mobile
   ```

3. **Configure Android build for NDK and Kotlin:**
   - In `android/app/build.gradle.kts`, set `minSdk = 28`, `compileSdk = 35`, `ndkVersion = "27.1.8937393"`.
   - Add `externalNativeBuild { cmake { path = "src/main/cpp/CMakeLists.txt" } }`.

4. **Add dependencies to `pubspec.yaml`:**
   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     flutter_riverpod: ^2.6.0
     go_router: ^14.6.0
     permission_handler: ^11.3.0
   dev_dependencies:
     pigeon: ^22.0.0
   ```

5. **Define the Pigeon API:**
   - Create `pigeon/echoecho_api.dart` with the initial interface: `startPipeline()`, `stopPipeline()`, `onStatusUpdate(Status status)`, `onLatencyUpdate(LatencyMetrics metrics)`.
   - Run `flutter pub run pigeon --input pigeon/echoecho_api.dart` to generate Dart and Kotlin stubs.

6. **Implement runtime permissions:**
   - On app launch, request `RECORD_AUDIO`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN`.
   - If any denied, show onboarding screen explaining why.

7. **Build and verify:**
   ```bash
   flutter build apk --debug
   flutter install
   ```
   - Confirm app launches on emulator and physical device without crashes.

8. **Create `tasks/phase2_todo.md`:**
   - Copy Milestone 1 checkboxes into a living task list.
   - Mark "Project initialized" as the first active task.

**Estimated time to Milestone 1 completion:** 3–5 days of focused work.

---

## Appendix A: Model Inventory for Phase 2

| Model | Purpose | Source Format | Mobile Format | Size (Mobile) | Location |
|---|---|---|---|---|---|
| Silero VAD v4.0 | Voice detection | ONNX | ONNX (already small) | ~1 MB | Download |
| Whisper tiny | STT | GGML / ONNX | GGML Q8_0 (whisper.cpp) | ~39 MB | Download |
| NLLB-200-distilled-600M | Translation | PyTorch | ONNX INT8 | ~600 MB | Download |
| Piper voices (en, ta, ja, zh) | TTS | ONNX | ONNX (already) | ~20–50 MB each | Download |

**Total download size:** ~750–850 MB on first run.  
**APK size (app only):** < 50 MB.

## Appendix B: Latency Budget (Mobile)

| Stage | Budget | Technique |
|---|---|---|
| Audio capture + VAD | 100–300ms | Streaming chunks, aggressive VAD |
| STT (Whisper tiny Q8_0) | 300–500ms | whisper.cpp, single-threaded or 2 threads |
| Translation (NLLB INT8) | 400–800ms | Small beam width, ONNX Runtime Mobile |
| TTS (Piper) | 100–300ms | Fast voice, streaming synthesis |
| Audio playback | 50–100ms | Oboe low-latency stream |
| **Total target** | **< 2s** | **< 1s aspirational on flagship** |

## Appendix C: Reference Devices

| Device | SoC | RAM | Target |
|---|---|---|---|
| Samsung Galaxy S24 | Snapdragon 8 Gen 3 | 8 GB | Primary dev + benchmark |
| Google Pixel 8 | Tensor G3 | 8 GB | Secondary test (pure Android) |
| Nothing Phone (2) | Snapdragon 8+ Gen 1 | 8 GB | Budget flagship test |
| Samsung Galaxy A54 | Exynos 1380 | 6 GB | Mid-range minimum viable test |
