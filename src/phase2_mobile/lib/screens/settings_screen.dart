import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/settings_provider.dart';
import '../widgets/language_selector.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final languagePair = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              LanguageSelector(
                label: 'Source language',
                value: languagePair.sourceCode,
                onChanged: notifier.setSourceLanguage,
              ),
              const SizedBox(height: 16),
              LanguageSelector(
                label: 'Target language',
                value: languagePair.targetCode,
                onChanged: notifier.setTargetLanguage,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
