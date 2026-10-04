import 'dart:async';

import 'package:flutter/services.dart';

import '../models/language_config.dart';

class OnDeviceTranslationService {
  static const _channel = MethodChannel('echoecho/translation');

  Future<String> translate({
    required String text,
    required LanguagePairConfig languages,
  }) async {
    if (text.trim().isEmpty || text.length > 4000) {
      throw const FormatException('Enter between 1 and 4,000 characters.');
    }
    if (languages.sourceCode == languages.targetCode) {
      throw const FormatException('Choose two different languages.');
    }

    final translation = await _channel.invokeMethod<String>('translate', {
      'text': text.trim(),
      'source': languages.sourceCode,
      'target': languages.targetCode,
    });
    if (translation == null || translation.trim().isEmpty) {
      throw const FormatException('The translation model returned no text.');
    }
    return translation.trim();
  }

  void cancel() {
    unawaited(_channel.invokeMethod<void>('cancel').catchError((Object _) {}));
  }
}
