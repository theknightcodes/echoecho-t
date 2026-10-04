# EthirOli mobile translation MVP

Android Flutter app with text input, on-device translation, native speech
recognition, Android text-to-speech playback, language swapping, copy, and a
50-turn session history. Supports 19 languages. Translation uses ML Kit's
on-device translation models; review transcripts and translations before
relying on them.

## Run

From this directory:

```sh
flutter pub get --enforce-lockfile
flutter run
```

Tap **Get started**, then type or tap **Speak**, review the text, and tap
**Translate**. Tap the speaker on a result to play it aloud. Swap languages to
reply. No server URL or API key is required.

The first translation with a language may download its model (about 30 MB per
language). Model downloads require an internet connection; after download,
translation runs on the phone and works offline. Only the translation model is
downloaded; submitted text is processed on-device. Model files remain on the
device. Conversation history stays in memory for the current session.

## Voice and privacy

Microphone permission is requested only when Speak is tapped. Denying it leaves
text translation available. Android's installed recognition service may send
audio to its provider; TTS may use online voices. Install target-language voices
in Android settings. Audio stops when the app backgrounds. This is a foreground,
turn-by-turn app, not continuous simultaneous interpretation.
Bluetooth routing, background microphone services and iOS voice support are not
implemented. The older Pigeon pipeline remains an unused experimental scaffold.

## Verify

```sh
flutter analyze
flutter test
flutter build apk --debug
```

Validation on 2026-09-24 predates the on-device translation integration: static
analysis passed, all 11 Flutter tests passed, and the Android debug APK built
successfully. The on-device model download and translation flow still require
physical-device validation.

Existing tests cover the previous Ollama service and conversation UI. They do not
validate ML Kit model downloads, offline translation, real microphone/TTS
behavior, or language quality. Test a physical device with network loss, denied
microphone permission, unavailable voices, and human-reviewed translations.

## Signed Play Console bundle

Release builds use an upload key configured in `android/key.properties`.
Copy `android/key.properties.example` when setting up a new development machine,
then restore your existing upload keystore and fill in its credentials. The
`storeFile` path is relative to `android/`, or may be absolute. Release builds
fail if the signing properties or keystore are missing; debug builds do not
require them.

```sh
flutter build appbundle --release
```

Upload `build/app/outputs/bundle/release/app-release.aab` to the Play Console
internal testing release, and wait for it to appear in the release's app bundle
list before proceeding to review. Each subsequent upload needs a new build
number (the number after `+` in `pubspec.yaml`).

Keep `android/upload-keystore.jks` and `android/key.properties` private and back
them up securely together. Both are ignored by Git. Reuse the same upload key
for updates; creating another key requires Play Console's upload-key reset
process once an upload certificate is registered. Google Play App Signing uses
a separate app signing key to sign installations delivered to testers.

API references: [ML Kit on-device translation](https://developers.google.com/ml-kit/language/translation/android),
[Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer).
