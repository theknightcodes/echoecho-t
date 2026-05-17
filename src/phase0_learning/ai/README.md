# Phase 0 — AI Inference (Week 2)

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| `whisper_benchmark.py` | Download + benchmark Whisper tiny STT | `python whisper_benchmark.py [audio.wav]` |

## Quick Start

```bash
# Run benchmark with synthetic 5s audio
python whisper_benchmark.py

# Run benchmark with your own audio file
python whisper_benchmark.py my_recording.wav
```

## Key Parameters

| Parameter | Value | Why |
|---|---|---|
| Model | Whisper tiny | 39M params; fastest Whisper variant |
| Compute type | int8 | Quantized; 2x faster than fp16 on CPU |
| Device | CPU | Baseline; MPS can be added later |
| Beam size | 5 | Quality/speed balance |

## Targets

| Check | Target | Measurement |
|---|---|---|
| Model load time | < 5s | `whisper_benchmark.py` |
| Transcription time | < 2s for 5s audio | `whisper_benchmark.py` |
| Real-time factor | > 2.5x | audio_duration / inference_time |

## Notes

- `faster-whisper` uses CTranslate2 backend for efficient inference
- For Phase 1, we may switch to ONNX Runtime if faster-whisper latency is too high
- The synthetic audio is speech-like but not real speech; real audio may yield different times
