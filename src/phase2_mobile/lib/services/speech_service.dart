import 'package:flutter/services.dart';

class SpeechService {
  static const _channel = MethodChannel('echoecho/speech');

  Future<String?> listen(String language) =>
      _channel.invokeMethod<String>('listen', {'language': language});

  Future<void> speak(String text, String language) => _channel
      .invokeMethod<void>('speak', {'text': text, 'language': language});

  Future<void> stop() => _channel.invokeMethod<void>('stop');
}
