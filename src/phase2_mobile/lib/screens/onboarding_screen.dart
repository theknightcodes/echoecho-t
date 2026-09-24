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
              const Icon(Icons.forum_outlined, size: 80),
              const SizedBox(height: 24),
              Text(
                'AetherOli',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 16),
              Text(
                'Make yourself understood.',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              const Text(
                'Choose from 19 languages and translate with your own LLM. Speak or type, review the translation, and play it aloud.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              const Text(
                'Connect an Ollama server to translate. Text goes to your configured server; voice recognition may use your device’s online service. Conversation history stays in memory for this session.',
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
