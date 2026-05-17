# Phase 0 — Mobile Audio Recorder (Week 3)

## Setup

1. Install Flutter: https://docs.flutter.dev/get-started/install
2. Run `flutter doctor` to verify setup
3. Install an Android emulator or connect a physical device

## Build & Run

```bash
cd src/phase0_learning/mobile/echoecho_t_audio
flutter pub get
flutter run
```

## What This App Does

- Requests microphone permission
- Records audio at 16kHz mono (same as our pipeline)
- Saves to app documents directory
- Plays back the recording
- Displays recording status

## Key Concepts Learned

- Flutter state management (Riverpod)
- Platform permissions (permission_handler)
- Audio recording (record package)
- Audio playback (audioplayers package)
- File paths on mobile (path_provider)

## Next Step

Once this runs successfully, we'll bridge to Kotlin native modules
for low-latency audio capture in Phase 2.
