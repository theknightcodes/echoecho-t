# Phase 0 — Audio Engineering (Week 1)

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| `audio_loopback.py` | Live loopback: mic → immediate speaker playback | `python audio_loopback.py [duration]` |
| `latency_benchmark.py` | Precise latency measurement using test tone bursts | `python latency_benchmark.py [duration]` |
| `buffer_benchmark.py` | Compare latency across different buffer sizes | `python buffer_benchmark.py` |
| `vad_test.py` | Live Silero VAD speech detection | `python vad_test.py [threshold] [min_duration_ms]` |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# 1. Test basic loopback (10 seconds)
python audio_loopback.py

# 2. Measure actual round-trip latency
python latency_benchmark.py 15

# 3. Find optimal buffer size
python buffer_benchmark.py

# 4. Test VAD with live microphone
python vad_test.py 0.5 250
```

## Key Parameters

| Parameter | Value | Why |
|---|---|---|
| Sample Rate | 16,000 Hz | Whisper default; good for speech |
| Block Size | 512 samples | ~32ms latency; balance of speed/quality |
| Channels | 1 (mono) | Sufficient for speech; halves data |
| VAD Threshold | 0.5 | Balanced sensitivity (tune per environment) |
| Min Speech Duration | 250 ms | Filters pops/clicks; captures words |

## Latency Targets

| Check | Target | Measurement Tool |
|---|---|---|
| Loopback latency | < 100 ms | `latency_benchmark.py` |
| Buffer chunk size | ~32 ms | `buffer_benchmark.py` |
| VAD detection delay | < 300 ms | `vad_test.py` (visual) |

## Notes

- Use headphones for loopback test to avoid feedback squeal
- For latency benchmark, remove headphones so mic hears speakers
- VAD threshold tuning: lower = more sensitive (catches whispers), higher = less false positives
- On macOS, you may need to grant microphone permission to Terminal/IDE
