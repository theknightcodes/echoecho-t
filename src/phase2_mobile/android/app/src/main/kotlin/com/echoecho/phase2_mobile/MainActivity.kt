package com.echoecho.phase2_mobile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.Translator
import com.google.mlkit.nl.translate.TranslatorOptions
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import java.util.Locale

class MainActivity : FlutterActivity() {
    private var recognizer: SpeechRecognizer? = null
    private var pending: MethodChannel.Result? = null
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var generation = 0
    private var activeTranslator: Translator? = null
    private var activeTranslationLanguages: Pair<String, String>? = null
    private var pendingTranslationResult: MethodChannel.Result? = null
    private var translationGeneration = 0
    private val handler = Handler(Looper.getMainLooper())
    private val timeout = Runnable { finishSpeech(null, "Listening timed out. Please try again.") }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        tts = TextToSpeech(this) { status -> ttsReady = status == TextToSpeech.SUCCESS }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "echoecho/speech")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "listen" -> listen(call.argument<String>("language") ?: "en", result)
                    "stop" -> { finishSpeech(null); tts?.stop(); result.success(null) }
                    "speak" -> {
                        val text = call.argument<String>("text") ?: ""
                        val language = call.argument<String>("language") ?: "en"
                        if (!ttsReady) {
                            result.error("tts_unavailable", "Speech output is not ready. Check Android text-to-speech settings.", null)
                        } else if (text.length > TextToSpeech.getMaxSpeechInputLength()) {
                            result.error("tts_length", "This translation is too long for spoken playback. Try a shorter phrase.", null)
                        } else if (tts!!.setLanguage(locale(language)) < TextToSpeech.LANG_AVAILABLE) {
                            result.error("tts_language", "Install a text-to-speech voice for this language in Android settings.", null)
                        } else {
                            val status = tts!!.speak(text, TextToSpeech.QUEUE_FLUSH, null, "translation")
                            if (status == TextToSpeech.ERROR) result.error("tts_failed", "Speech playback could not start.", null)
                            else result.success(null)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "echoecho/translation")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "translate" -> translate(call, result)
                    "cancel" -> {
                        cancelTranslation()
                        result.success(null)
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun translate(call: MethodCall, result: MethodChannel.Result) {
        val text = call.argument<String>("text")?.trim().orEmpty()
        val sourceTag = call.argument<String>("source").orEmpty()
        val targetTag = call.argument<String>("target").orEmpty()
        if (text.isEmpty() || text.length > 4000) {
            result.error("invalid_text", "Enter between 1 and 4,000 characters.", null)
            return
        }
        if (sourceTag == targetTag) {
            result.error("invalid_languages", "Choose two different languages.", null)
            return
        }
        val source = TranslateLanguage.fromLanguageTag(sourceTag)
        val target = TranslateLanguage.fromLanguageTag(targetTag)
        if (source == null || target == null) {
            result.error("unsupported_language", "Offline translation is not available for this language.", null)
            return
        }

        cancelTranslation()
        val requestGeneration = translationGeneration
        pendingTranslationResult = result
        val languages = source to target
        try {
            if (activeTranslationLanguages != languages) {
                activeTranslator?.close()
                activeTranslator = Translation.getClient(
                    TranslatorOptions.Builder()
                        .setSourceLanguage(source)
                        .setTargetLanguage(target)
                        .build()
                )
                activeTranslationLanguages = languages
            }
            val translator = activeTranslator ?: run {
                completeTranslationError(requestGeneration, "translation_failed", "The offline translation model could not start.")
                return
            }
            translator.downloadModelIfNeeded(DownloadConditions.Builder().build())
                .addOnSuccessListener download@{
                    if (requestGeneration != translationGeneration) return@download
                    translator.translate(text)
                        .addOnSuccessListener translationComplete@{ translated ->
                            if (requestGeneration != translationGeneration) return@translationComplete
                            val pending = pendingTranslationResult
                            pendingTranslationResult = null
                            pending?.success(translated)
                        }
                        .addOnFailureListener {
                            completeTranslationError(requestGeneration, "translation_failed", "On-device translation failed. Please try again.")
                        }
                }
                .addOnFailureListener {
                    completeTranslationError(requestGeneration, "model_download", "Couldn't download the offline language model. Connect to the internet and try again.")
                }
        } catch (error: Exception) {
            Log.e("EthirOliTranslate", "Could not start translation for $sourceTag -> $targetTag", error)
            completeTranslationError(
                requestGeneration,
                "translation_start_failed",
                "Translation could not start. Update Google Play services, connect to the internet for the first model download, and check available storage."
            )
        }
    }

    private fun completeTranslationError(generation: Int, code: String, message: String) {
        if (generation != translationGeneration) return
        val pending = pendingTranslationResult
        pendingTranslationResult = null
        pending?.error(code, message, null)
    }

    private fun cancelTranslation() {
        translationGeneration++
        val pending = pendingTranslationResult
        pendingTranslationResult = null
        pending?.error("cancelled", "Translation cancelled.", null)
    }

    private fun locale(code: String): Locale = Locale.forLanguageTag(when (code) {
        "en" -> "en-US"
        "ta" -> "ta-IN"
        "es" -> "es-ES"
        "fr" -> "fr-FR"
        "hi" -> "hi-IN"
        "zh" -> "zh-CN"
        "ja" -> "ja-JP"
        "ar" -> "ar-SA"
        "pt" -> "pt-PT"
        "de" -> "de-DE"
        "bn" -> "bn-BD"
        "id" -> "id-ID"
        "ko" -> "ko-KR"
        "ru" -> "ru-RU"
        "it" -> "it-IT"
        "tr" -> "tr-TR"
        "vi" -> "vi-VN"
        "th" -> "th-TH"
        "ur" -> "ur-PK"
        else -> code
    })

    private fun listen(language: String, result: MethodChannel.Result) {
        if (pending != null) { result.error("busy", "Speech recognition is already running.", null); return }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            result.error("permission", "Microphone access is required for speech input.", null); return
        }
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            result.error("unavailable", "No speech recognition service is installed. Type your message instead.", null); return
        }
        tts?.stop()
        pending = result
        val session = ++generation
        try {
            recognizer = SpeechRecognizer.createSpeechRecognizer(this)
            recognizer!!.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
                override fun onError(error: Int) {
                    if (session != generation) return
                    val message = when (error) {
                        SpeechRecognizer.ERROR_NO_MATCH, SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech detected. Please try again."
                        SpeechRecognizer.ERROR_NETWORK, SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Speech recognition needs a network connection. You can type instead."
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Microphone permission was denied."
                        else -> "Speech recognition failed ($error). Try again or type your message."
                    }
                    finishSpeech(null, message)
                }
                override fun onResults(results: Bundle?) {
                    if (session != generation) return
                    val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                    finishSpeech(text, if (text.isNullOrBlank()) "No speech detected. Please try again." else null)
                }
            })
            recognizer!!.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, locale(language).toLanguageTag())
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            })
            handler.postDelayed(timeout, 30000)
        } catch (_: Exception) {
            finishSpeech(null, "Speech input could not start. Try typing instead.")
        }
    }

    private fun finishSpeech(text: String?, error: String? = null) {
        generation++
        handler.removeCallbacks(timeout)
        val result = pending
        pending = null
        val previous = recognizer
        recognizer = null
        previous?.cancel()
        previous?.destroy()
        if (error != null) result?.error("speech", error, null) else result?.success(text)
    }

    override fun onStop() {
        finishSpeech(null)
        tts?.stop()
        super.onStop()
    }

    override fun onDestroy() {
        finishSpeech(null)
        cancelTranslation()
        activeTranslator?.close()
        activeTranslator = null
        activeTranslationLanguages = null
        tts?.shutdown()
        tts = null
        super.onDestroy()
    }
}
