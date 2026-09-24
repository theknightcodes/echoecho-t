# AetherOli mobile translation MVP

Android Flutter app with text input, native speech recognition, Ollama-powered
translation, Android text-to-speech playback, language swapping, copy, and a
50-turn session history. Supports English, Tamil, Japanese and Chinese; actual
recognition, voice availability and translation quality depend on your device
and chosen model. Review speech transcripts before submitting them.

## Run

1. Install and start Ollama on your computer. Install a multilingual model suitable
   for your hardware and languages. Use `ollama list` to get its exact name.
2. From this directory:

   ```sh
   flutter pub get --enforce-lockfile
   flutter run --dart-define=OLLAMA_URL=http://10.0.2.2:11434 --dart-define=OLLAMA_MODEL=YOUR_INSTALLED_MODEL
   ```

   `10.0.2.2` reaches the host computer from the standard Android emulator.
   For a USB-connected phone, use `adb reverse tcp:11434 tcp:11434` and configure
   `http://127.0.0.1:11434` instead. This avoids exposing Ollama on your network.
3. Tap **Get started**, then the toolbar connection icon to change the server or
   model. Type or tap **Speak**, review the text, then **Translate**. Tap the
   speaker on a result to play the translation. Swap languages to reply.

Connection settings can also be entered entirely in the app. They and conversation
history are in memory only; restarting the app resets them to build defaults.
Only the current submitted phrase is sent to the LLM, not previous conversation
history. No paid API key is bundled. Direct authenticated cloud APIs are not
implemented. Do not expose an unauthenticated Ollama server to the internet.

HTTP is enabled only in Android debug builds for local development; use HTTPS
for release connections. The client uses Ollama's `/api/chat`, with non-streaming
responses, a 90-second timeout, bounded input/output, and explicit error states.
Cancel closes the mobile connection and ignores late results; the server may
continue inference until it observes the disconnect.

## Voice and privacy

Microphone permission is requested only when Speak is tapped. Denying it leaves
text translation available. Android's installed recognition service may send
audio to its provider; TTS may use online voices. Install target-language voices
in Android settings. Audio stops when the app backgrounds. This is a foreground,
turn-by-turn app, not continuous simultaneous interpretation or an on-device LLM.
Bluetooth routing, background microphone services and iOS voice support are not
implemented. The older Pigeon pipeline remains an unused experimental scaffold.

## Verify

```sh
flutter analyze
flutter test
flutter build apk --debug
```

Validation on 2026-09-24: static analysis passed, all 11 Flutter tests passed,
and the Android debug APK built successfully. No Android device or Ollama
installation was available for live end-to-end validation.

Tests cover HTTP payloads/Unicode, invalid inputs, server and truncated-response
errors, conversation history, and cancellation. A successful build does not
validate real microphone/TTS behavior or language quality. Test a physical device
with permission denial, backgrounding, network loss, unavailable voices, and
human-reviewed translations before release. Production signing remains required.

API references: [Ollama chat](https://docs.ollama.com/api/chat),
[Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer).
