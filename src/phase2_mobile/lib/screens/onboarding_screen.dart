import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: Image.asset(
                  'assets/branding/aetheroli_app_icon.png',
                  width: 112,
                  height: 112,
                  fit: BoxFit.cover,
                  semanticLabel: 'EthirOli app icon',
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'EthirOli',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 16),
              Text(
                'Make yourself understood.',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              const Text(
                'Translate between 19 languages with an on-device translation model. Speak or type, review the translation, and play it aloud.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              const Text(
                'The first time you use a language, its translation model downloads to your phone (about 30 MB). After that, translation runs on your device. Speech recognition may use your device’s online service.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: () => context.go('/home'),
                child: const Text('Get started'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
