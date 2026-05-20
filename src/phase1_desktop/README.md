# Phase 1 — Desktop Prototype

## Pipeline Architecture

```
Mic → AudioCapture → VAD → STT → [Switch Check] → Translation → TTS → Speaker
```

## Modules

| Module | File | Purpose |
|---|---|---|
| Audio Capture | `audio/capture.py` | Stream mic input to queue |
| Audio Playback | `audio/playback.py` | Play audio from queue |
| VAD | `ai/vad.py` | Silero VAD speech detection |
| STT | `ai/stt.py` | Whisper tiny transcription |
| Translation | `ai/translate.py` | NLLB-200-distilled-600M (single model) |
| Language Manager | `ai/language_manager.py` | Multi-language switching |
| TTS | `ai/tts.py` | Text-to-speech (pyttsx3) |
| Orchestrator | `pipeline/orchestrator.py` | Threaded pipeline controller |
| Orchestrator v2 | `pipeline/orchestrator_v2.py` | Pipeline + language switching |
| Latency | `utils/latency.py` | Per-stage timing + CSV logging |

## Usage

```bash
cd src/phase1_desktop

# Default: English → German, 30 seconds
python main.py

# Custom duration + language
python main.py 60 fr     # 60s, start with French
python main.py 60 ja     # 60s, start with Japanese
python main.py 60 hi     # 60s, start with Hindi
```

### Voice Commands (During Runtime)

Say any of these to switch languages:
- "switch to French"
- "change to Spanish"
- "speak Japanese"
- "use Hindi"
- "German"

The system responds with a confirmation in the target language.

### Supported Languages

| Code | Language | QA Status |
|---|---|---|
| de | German | PASS |
| fr | French | PASS |
| es | Spanish | PASS |
| it | Italian | PASS |
| pt | Portuguese | PASS |
| nl | Dutch | PASS |
| ru | Russian | PASS |
| zh | Chinese | PASS |
| ja | Japanese | PASS |
| ko | Korean | PASS |
| ta | Tamil | PASS |
| hi | Hindi | PASS |
| ar | Arabic | PASS |
| tr | Turkish | PASS |
| pl | Polish | PASS |

## Testing

```bash
# Unit tests
python -m pytest tests/

# Manual test with synthetic audio
python tests/test_pipeline.py
```

## Latency Logging

Results are saved to `logs/latency.csv`. View with:

```bash
python -c "from utils.latency import LatencyLogger; LatencyLogger().report()"
```

## Targets

| Stage | Target | Current |
|---|---|---|
| VAD | < 300ms | TBD |
| STT | < 1s for 5s audio | 0.15s |
| Translation | < 500ms | TBD |
| TTS | < 200ms | TBD |
| **Total** | **< 3s** | TBD |

## Notes

- TTS uses pyttsx3 (system voices) in Phase 1. Piper TTS in Phase 2.
- Translation uses NLLB-200-distilled-600M (~2.4GB fp16) — single model for 15 languages.
- Whisper tiny downloads on first run (~39MB).
- All processing is local — no cloud calls.
