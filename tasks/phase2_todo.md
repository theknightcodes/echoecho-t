# Phase 2 — Living Task List

Source: docs/PHASE2_PLAN.md

---

## Milestone 1: Flutter App Skeleton with Audio Permissions — Week 1

- [x] Flutter project initialized at `src/phase2_mobile/`
- [x] AndroidManifest.xml includes `RECORD_AUDIO`, `BLUETOOTH`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_MICROPHONE` permissions
- [x] Runtime permission flow implemented (Android 6+ dynamic permissions) — onboarding_screen.dart
- [x] Basic navigation scaffold: Home, Settings, Onboarding (+ language-pair route)
- [x] State management (Riverpod) wired up with placeholder providers (pipeline, settings, bluetooth)
- [x] Pigeon platform channel defined and generated (Dart <-> Kotlin stub)
- [x] App builds and runs on Android emulator (Pixel 7, API 36) — verified via adb install + screenshots
- [ ] Physical device verification (Samsung S24 or equivalent) — not available in this environment
- [ ] CI: `flutter build apk --release` passes in GitHub Actions — no CI workflow exists yet in this repo

**Key Output:** Installable APK with working UI shell and permission flows. ACHIEVED (debug build).

**Environment setup performed this session:**
- Installed Flutter 3.44.7 via `brew install --cask flutter`
- Installed Android cmdline-tools via `brew install --cask android-commandlinetools`, symlinked into `~/Library/Android/sdk/cmdline-tools/latest`
- Accepted Android SDK licenses
- Installed NDK 28.2.13676358 (r28c) — Gradle's AGP-preferred version; plan's suggested "27b+" line is satisfied by any 27+, we're on 28 since that's what this AGP version resolved to
- No system Java was present; builds must run with `JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"` since Temurin cask installation requires interactive sudo (skipped)

**Deviations from plan:**
- `minSdk`/`targetSdk`/`compileSdk` set explicitly (28/35/35) instead of `flutter.*` defaults, per plan section 2.1
- `ndkVersion` is 28.2.13676358, not the plan's literal "27.1.8937393" (that exact NDK doesn't exist; Gradle requested 28.2.13676358 and it satisfies "27b+")

---

## Milestone 2: Native Android Audio Capture Service — Week 2-3
- [ ] Not started

## Milestone 3: Whisper STT Integration — Week 4-5
- [ ] Not started

## Milestone 4: NLLB Translation Integration — Week 6-7
- [ ] Not started

## Milestone 5: TTS Integration — Week 8
- [ ] Not started

## Milestone 6: Full Pipeline Wiring — Week 9
- [ ] Not started

## Milestone 7: Offline Mode Verification — Week 10
- [ ] Not started

## Milestone 8: Real-World Testing — Week 11-12
- [ ] Not started
