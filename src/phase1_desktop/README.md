# Phase 1 — Desktop Prototype

## Pipeline Architecture

```
Mic → AudioCapture → VAD → STT → Translation → TTS → Speaker
```

## Modules

| Module | File | Purpose |
|---|---|---|
| Audio Capture | `audio/capture.py` | Stream mic input to queue |
| Audio Playback | `audio/playback.py` | Play audio from queue |
| VAD | `ai/vad.py` | Silero VAD speech detection |
| STT | `ai/stt.py` | Whisper tiny transcription |
| Translation | `ai/translate.py` | Helsinki-NLP translation |
| TTS | `ai/tts.py` | Text-to-speech (pyttsx3) |
| Orchestrator | `pipeline/orchestrator.py` | Threaded pipeline controller |
| Latency | `utils/latency.py` | Per-stage timing + CSV logging |

## Usage

```bash
cd src/phase1_desktop
python main.py [duration_seconds]
```

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
- Translation model downloads on first run (~300MB).
- Whisper tiny downloads on first run (~39MB).
- All processing is local — no cloud calls.
