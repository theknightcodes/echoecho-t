class LanguageOption {
  const LanguageOption(this.code, this.label);

  final String code;
  final String label;
}

/// Common language choices supported by multilingual translation models.
/// Actual quality depends on the model configured by the user.
const supportedLanguages = <LanguageOption>[
  LanguageOption('en', 'English'),
  LanguageOption('ta', 'Tamil'),
  LanguageOption('es', 'Spanish'),
  LanguageOption('fr', 'French'),
  LanguageOption('hi', 'Hindi'),
  LanguageOption('zh', 'Chinese (Simplified)'),
  LanguageOption('ja', 'Japanese'),
  LanguageOption('ar', 'Arabic'),
  LanguageOption('pt', 'Portuguese'),
  LanguageOption('de', 'German'),
  LanguageOption('bn', 'Bengali'),
  LanguageOption('id', 'Indonesian'),
  LanguageOption('ko', 'Korean'),
  LanguageOption('ru', 'Russian'),
  LanguageOption('it', 'Italian'),
  LanguageOption('tr', 'Turkish'),
  LanguageOption('vi', 'Vietnamese'),
  LanguageOption('th', 'Thai'),
  LanguageOption('ur', 'Urdu'),
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
