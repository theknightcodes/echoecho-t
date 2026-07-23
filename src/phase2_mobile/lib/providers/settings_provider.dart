import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/language_config.dart';

class SettingsNotifier extends StateNotifier<LanguagePairConfig> {
  SettingsNotifier() : super(const LanguagePairConfig());

  void setSourceLanguage(String code) {
    state = state.copyWith(sourceCode: code);
  }

  void setTargetLanguage(String code) {
    state = state.copyWith(targetCode: code);
  }
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, LanguagePairConfig>((ref) {
  return SettingsNotifier();
});
