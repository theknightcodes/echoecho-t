import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'settings_screen.dart';

/// Alias route for picking the language pair from onboarding/home;
/// reuses the same widget as the Settings language pickers.
class LanguagePairScreen extends StatelessWidget {
  const LanguagePairScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Choose languages'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: const SettingsScreen(),
    );
  }
}
