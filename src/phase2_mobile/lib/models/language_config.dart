class LanguageOption {
  const LanguageOption(this.code, this.label);

  final String code;
  final String label;
}

/// Phase 1 priority languages (docs/PHASES.md).
const supportedLanguages = <LanguageOption>[
  LanguageOption('en', 'English'),
  LanguageOption('ta', 'Tamil'),
  LanguageOption('ja', 'Japanese'),
  LanguageOption('zh', 'Chinese'),
];

class LanguagePairConfig {
  const LanguagePairConfig({this.sourceCode = 'en', this.targetCode = 'ta'});

  final String sourceCode;
  final String targetCode;

  LanguagePairConfig copyWith({String? sourceCode, String? targetCode}) {
    return LanguagePairConfig(
      sourceCode: sourceCode ?? this.sourceCode,
      targetCode: targetCode ?? this.targetCode,
    );
  }
}
