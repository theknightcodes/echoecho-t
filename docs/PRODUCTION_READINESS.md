# Production readiness review — 2026-09-24

**Mobile implementation update:** A foreground Android speech/text translation
flow now uses a configurable Ollama server and Android speech recognition/TTS.
The original review below records the earlier scaffold baseline; its claims
that mobile translation is entirely absent and onboarding requires Bluetooth
are superseded. The older continuous Pigeon pipeline, background operation,
Bluetooth routing, on-device LLM and physical-device acceptance remain unfinished.
See [mobile setup and current limitations](../src/phase2_mobile/README.md).

**Release decision: not ready for production.** This repository contains learning
experiments, a desktop prototype, and an Android UI scaffold. Successful unit tests
and APK compilation do not establish translation quality, offline operation, or
mobile pipeline functionality.

## Validation performed

Environment: macOS, Python 3.14.3 (existing project venv), Flutter 3.44.7,
Dart 3.12.2. Hardware audio capture and cloud synthesis were not exercised.

| Check | Result |
| --- | --- |
| Desktop deterministic regression suite | 17 tests passed |
| Flutter widget/state regression suite | 5 tests passed |
| Flutter static analysis | Passed |
| Android debug APK | Built successfully |
| Python compilation | Passed |
| Existing Python environment `pip check` | Passed |
| Git whitespace validation | Passed |
| CI workflow | Added; remote execution not yet verified |
| Real microphone / speaker / Bluetooth / battery / translation quality | Not validated |
| Vulnerability database audit / clean full inference installation | Not performed |

Tests use fake native services and mocked model constructors. They validate error
handling and buffer behavior, not model outputs. The older files under
`src/phase1_desktop/tests/` are manual integration/diagnostic scripts; some print
PASS without asserting semantic correctness and some access audio/network at
import or runtime. They are not part of the deterministic release checks.

## Fixes delivered

- Removed invalid `gnumpy` dependency.
- Playback now uses the correct NumPy output stream, preserves audio across
  callbacks, supports all configured channels, pads silence, validates samples,
  copies caller data, and reports queue rejection.
- Capture overflow now removes the oldest sample block as documented. Failed
  stream startup closes resources; repeated start does not open another stream.
- Pipeline rejects unsupported sample rates, closes TTS after capture startup
  failure, avoids duplicate starts, and rejects reuse after shutdown.
- Microphone processing pauses while TTS is pending/active; VAD resets are
  performed by the VAD worker rather than concurrently by the processing worker.
  Cooldown uses a monotonic clock. This is feedback mitigation, not acoustic echo
  cancellation; physical-device validation remains necessary.
- Ordinary short phrases are no longer discarded by a hard-coded word blacklist.
- Language selection no longer downloads a model. Unsupported translation
  targets fail before loading; commands accept sentence-ending punctuation.
- TTS network access requires explicit `TTS(allow_network=True)` opt-in. Cloud
  synthesis has a request timeout. Text goes to `say` via stdin, preserving
  decimals, negative signs, contractions and sentence punctuation.
- Desktop runtime errors now return a failing exit status.
- Flutter reports failed start/stop operations, permits retry after startup
  failure, suppresses duplicate starts, and avoids state updates after disposal.
  Home renders errors rather than falsely claiming that the pipeline is running.
- Permission-request exceptions restore the onboarding button. Onboarding
  identifies the app as a preview rather than claiming offline translation works.
- Android release builds no longer inherit debug signing credentials.
- Added deterministic tests and GitHub Actions QA. Fixed the manual E2E runner's
  repository-root venv path.

## Remaining findings, in priority order

### P0 — Mobile translation is absent

`src/phase2_mobile/android/app/src/main/kotlin/com/echoecho/phase2_mobile/MainActivity.kt`
only extends `FlutterActivity`. It does not register `EchoEchoHostApi` or implement
capture, VAD, STT, translation, TTS, or foreground service lifecycle. The Dart
status/latency callback interface is also not registered. Bluetooth state and
latency UI are placeholders. No amount of Flutter analysis can establish this
missing functionality.

Required: implement the native engine with tested model assets, explicit lifecycle
ownership and cancellation, status/latency events, audio focus and routing, and
foreground microphone service behavior before enabling production conversation UX.

### P0 — Translation model is not a cleared commercial dependency

`src/phase1_desktop/ai/language_manager.py` uses
`facebook/nllb-200-distilled-600M`. Its [publisher model card](https://huggingface.co/facebook/nllb-200-distilled-600M/blob/main/README.md)
lists CC-BY-NC-4.0. Commercial release requires a suitably licensed replacement
or appropriate rights, followed by language-quality validation. No replacement
was selected automatically because licensing, language coverage and quality are
product requirements that this repository does not resolve.

### P1 — Model installation is not reproducible or fully offline

`ai/vad.py` executes code loaded through `torch.hub.load` from a mutable repository
reference with `trust_repo=True`. Whisper and NLLB use unpinned model references;
Python application dependencies use open version ranges. CI pins its minimal unit
test dependencies only, not the application dependency graph. Bundle reviewed,
checksum-verified models, pin revisions and transitive dependencies, and test a
clean installation with networking disabled. Do not equate `pip check` with a
security audit or proof that a fresh install works.

### P1 — Shutdown and worker failure handling need redesign

`pipeline/orchestrator_v2.py` joins workers for two seconds but does not cancel
model inference. `ai/tts.py` cannot interrupt an active `say` process or all
network/playback operations at shutdown. A late transcript can race with queue
clearing. VAD errors and user callbacks can still terminate worker threads without
coordinated pipeline failure. Require cancellable lifecycle ownership (process
isolation if necessary), generation/session identifiers, bounded shutdown,
visible failure status, and stress tests before long-running use. The older
`pipeline/orchestrator.py` also lacks equivalent safeguards and should not be used
as a production entry point.

### P1 — Offline speech output is platform-dependent

Network synthesis now defaults off. macOS `say` needs installed target-language
voices; other platforms currently fall back to printed text. Vendor and validate
an offline TTS engine for supported platforms. Enabling Edge TTS transmits text
to an external service and needs clear product consent and service suitability
review. The current network timeout does not bound total playback time.

### P1 — Android permissions and release lifecycle are incomplete

Onboarding requests Bluetooth permissions on all Android versions, including
versions predating those runtime permissions, and treats Bluetooth as mandatory.
Test API 28–30 and 31+, support permanently denied permissions with Settings
recovery, and request Bluetooth access only when its feature is used. Test
permission revocation, backgrounding, screen lock, audio focus interruptions,
Bluetooth disconnects and low-memory recovery. Configure private production
signing outside version control; release artifacts are now unsigned by default.

### P2 — Quality, observability and UX gaps

- No objective speech-recognition or translation acceptance corpus, human review
  across the advertised languages, or noisy-room evaluation.
- Desktop latency reporting sums averages from different stage populations;
  this is not measured utterance end-to-end latency. TTS playback and queue delay
  are not measured by the active pipeline. Add utterance IDs and monotonic timing
  from speech completion through actual playback.
- CSV metrics perform synchronous file writes in hot paths, have no rotation,
  and concurrent record iteration is not fully protected. Add bounded buffering,
  retention limits and thread-safe snapshots.
- Language/settings state is not persisted, identical language pairs are allowed,
  and native failures currently have a generic explanation.
- Stopping while mobile startup is pending is ignored. Background disposal does
  not yet own/stop a future native engine. Complete this with native lifecycle work.
- Desktop transcripts are printed to the terminal; redirected output may retain
  conversation content. Define an explicit diagnostic logging/retention policy.
- Documentation in `SECURITY.md` and `docs/SECURITY.md` describes intended controls,
  not evidence of implementation. Older phase status/QA tables were aspirational.

## Repeatable QA

From the repository root, using the existing venv:

```sh
venv/bin/python -m unittest discover -s tests/unit -v
venv/bin/python -m compileall -q src/phase1_desktop
venv/bin/python -m pip check
cd src/phase2_mobile
flutter pub get --enforce-lockfile
flutter analyze
flutter test
flutter build apk --debug
```

`.github/workflows/qa.yml` runs the deterministic checks on pushes and PRs.
It does not run microphone or external-service diagnostics. A debug APK is not
an accepted or signed production release artifact.

## Release acceptance still required

1. Resolve model rights and select supported platforms/languages. Package and
   verify models, dependencies, offline installation and update behavior.
2. Implement the native mobile pipeline and lifecycle; validate failure and
   cancellation paths without fictitious successful states.
3. Exercise each supported Android/API/device combination with built-in audio
   and target earbuds. Verify permission denial/revocation, reconnects,
   interruptions and repeated start/stop, including startup cancellation.
4. Run a consented reference speech corpus across every advertised language;
   measure accuracy, human-rated meaning preservation, p50/p95 utterance latency,
   memory, battery, thermal throttling and a multi-hour soak.
5. Complete dependency vulnerability and artifact review, configure release
   signing, test the release build on physical devices, and archive results.
