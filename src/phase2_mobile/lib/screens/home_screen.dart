import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';

import '../models/language_config.dart';
import '../services/on_device_translation_service.dart';
import '../services/speech_service.dart';
import '../services/translation_service.dart';

class ConversationTurn {
  const ConversationTurn(this.original, this.translation, this.languages);
  final String original;
  final String translation;
  final LanguagePairConfig languages;
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, this.translationService, this.speechService});
  final TranslationService? translationService;
  final SpeechService? speechService;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final _text = TextEditingController();
  final _history = <ConversationTurn>[];
  late final _deviceTranslator = OnDeviceTranslationService();
  late final _speech = widget.speechService ?? SpeechService();
  var _languages = const LanguagePairConfig();
  bool _translating = false;
  bool _listening = false;
  String? _error;
  int _generation = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused) {
      _generation++;
      _cancelTranslation();
      unawaited(_speech.stop().catchError((Object _) {}));
      setState(() {
        _listening = false;
        _translating = false;
      });
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _generation++;
    _cancelTranslation();
    unawaited(_speech.stop().catchError((Object _) {}));
    _text.dispose();
    super.dispose();
  }

  void _cancelTranslation() {
    widget.translationService?.cancel();
    _deviceTranslator.cancel();
  }

  String _label(String code) =>
      supportedLanguages.firstWhere((l) => l.code == code).label;

  Future<void> _translate() async {
    if (_translating || _listening) return;
    final original = _text.text.trim();
    final pair = _languages;
    final generation = ++_generation;
    setState(() {
      _translating = true;
      _error = null;
    });
    try {
      final translated = widget.translationService == null
          ? await _deviceTranslator.translate(text: original, languages: pair)
          : await widget.translationService!.translate(
              endpoint: '',
              model: '',
              text: original,
              languages: pair,
            );
      if (!mounted || generation != _generation) return;
      setState(() {
        _history.insert(0, ConversationTurn(original, translated, pair));
        if (_history.length > 50) _history.removeLast();
        _text.clear();
      });
    } catch (e) {
      if (mounted && generation == _generation) {
        setState(
          () => _error = switch (e) {
            FormatException() => e.message,
            TimeoutException() =>
              'On-device translation took too long. Try a shorter phrase.',
            SocketException() =>
              'Cannot prepare the offline translation model. Check your internet connection and try again.',
            HttpException() => e.message,
            PlatformException() =>
              e.message ?? 'On-device translation failed. Please try again.',
            _ => 'On-device translation failed. Please try again.',
          },
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _translating = false);
      }
    }
  }

  Future<void> _listen() async {
    final generation = ++_generation;
    setState(() {
      _listening = true;
      _error = null;
    });
    try {
      final permission = await Permission.microphone.request();
      if (!mounted || generation != _generation) return;
      if (!permission.isGranted) {
        setState(
          () => _error =
              'Microphone access is disabled. Enable it in Android app settings, or type below.',
        );
        return;
      }
      final transcript = await _speech.listen(_languages.sourceCode);
      if (mounted && generation == _generation && transcript != null) {
        _text.text = transcript;
      }
    } catch (e) {
      if (mounted && generation == _generation) {
        setState(
          () => _error = e is PlatformException
              ? e.message
              : 'Speech input is unavailable. You can still type.',
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _listening = false);
      }
    }
  }

  Future<void> _stop() async {
    _generation++;
    _cancelTranslation();
    setState(() {
      _listening = false;
      _translating = false;
    });
    try {
      await _speech.stop();
    } catch (_) {
      /* Text translation remains available. */
    }
  }

  Future<void> _speak(ConversationTurn turn) async {
    try {
      await _speech.speak(turn.translation, turn.languages.targetCode);
    } catch (e) {
      if (mounted) {
        setState(
          () => _error = e is PlatformException
              ? e.message
              : 'Spoken playback is unavailable on this device.',
        );
      }
    }
  }

  Widget _language(String code, bool source) => Expanded(
    child: DropdownButtonFormField<String>(
      key: ValueKey('${source}_$code'),
      initialValue: code,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: source ? 'You speak' : 'Translate to',
        border: const OutlineInputBorder(),
      ),
      items: [
        for (final language in supportedLanguages)
          DropdownMenuItem(value: language.code, child: Text(language.label)),
      ],
      onChanged: _translating || _listening
          ? null
          : (value) {
              if (value == null) return;
              setState(() {
                if (source) {
                  _languages = LanguagePairConfig(
                    sourceCode: value,
                    targetCode: value == _languages.targetCode
                        ? _languages.sourceCode
                        : _languages.targetCode,
                  );
                } else {
                  _languages = LanguagePairConfig(
                    sourceCode: value == _languages.sourceCode
                        ? _languages.targetCode
                        : _languages.sourceCode,
                    targetCode: value,
                  );
                }
              });
            },
    ),
  );

  @override
  Widget build(BuildContext context) {
    final busy = _translating || _listening;
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('EthirOli')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'A little closer.\nIn any language.',
              style: Theme.of(
                context,
              ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text('Speak or type, review your words, then translate.'),
            const SizedBox(height: 24),
            Row(
              children: [
                _language(_languages.sourceCode, true),
                IconButton(
                  tooltip: 'Swap languages',
                  onPressed: busy
                      ? null
                      : () => setState(
                          () => _languages = LanguagePairConfig(
                            sourceCode: _languages.targetCode,
                            targetCode: _languages.sourceCode,
                          ),
                        ),
                  icon: const Icon(Icons.swap_horiz),
                ),
                _language(_languages.targetCode, false),
              ],
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _text,
              enabled: !busy,
              minLines: 3,
              maxLines: 7,
              maxLength: 4000,
              decoration: const InputDecoration(
                hintText: 'What would you like to say?',
                border: OutlineInputBorder(),
              ),
            ),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: _translating
                      ? null
                      : (_listening ? _stop : _listen),
                  icon: Icon(_listening ? Icons.stop : Icons.mic_none),
                  label: Text(_listening ? 'Stop' : 'Speak'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: busy ? null : _translate,
                    icon: const Icon(Icons.translate),
                    label: Text(_translating ? 'Translating…' : 'Translate'),
                  ),
                ),
              ],
            ),
            if (busy) ...[
              const SizedBox(height: 12),
              const LinearProgressIndicator(),
              Text(
                _listening
                    ? 'Listening… Your transcript will appear above.'
                    : 'Preparing on-device translation…',
              ),
              if (_translating)
                TextButton(onPressed: _stop, child: const Text('Cancel')),
            ],
            if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(
                  _error!,
                  style: TextStyle(color: colors.error),
                  semanticsLabel: _error,
                ),
              ),
            const SizedBox(height: 8),
            const Text(
              'Speech input may use your device’s online recognition service. Review translations before relying on them.',
              style: TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Conversation',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                if (_history.isNotEmpty)
                  TextButton(
                    onPressed: () {
                      _stop();
                      setState(() => _history.clear());
                    },
                    child: const Text('Clear'),
                  ),
              ],
            ),
            if (_history.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 28),
                child: Text(
                  'Your translations will appear here.\nHistory stays in memory for this session.',
                  textAlign: TextAlign.center,
                ),
              ),
            for (final turn in _history)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${_label(turn.languages.sourceCode)} → ${_label(turn.languages.targetCode)}',
                        style: TextStyle(color: colors.primary),
                      ),
                      const SizedBox(height: 8),
                      SelectableText(turn.original),
                      const Divider(),
                      SelectableText(
                        turn.translation,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          IconButton(
                            tooltip: 'Copy translation',
                            icon: const Icon(Icons.copy),
                            onPressed: () async {
                              await Clipboard.setData(
                                ClipboardData(text: turn.translation),
                              );
                            },
                          ),
                          IconButton(
                            tooltip: 'Play translation',
                            icon: const Icon(Icons.volume_up_outlined),
                            onPressed: busy ? null : () => _speak(turn),
                          ),
                          IconButton(
                            tooltip: 'Stop playback',
                            icon: const Icon(Icons.stop_circle_outlined),
                            onPressed: _stop,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
