import 'package:flutter/material.dart';

import '../models/language_config.dart';

class LanguageSelector extends StatelessWidget {
  const LanguageSelector({
    super.key,
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: [
        for (final lang in supportedLanguages)
          DropdownMenuItem(value: lang.code, child: Text(lang.label)),
      ],
      onChanged: (code) {
        if (code != null) onChanged(code);
      },
    );
  }
}
