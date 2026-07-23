import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:permission_handler/permission_handler.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  bool _requesting = false;
  String? _denialMessage;

  Future<void> _requestPermissions() async {
    setState(() {
      _requesting = true;
      _denialMessage = null;
    });

    final statuses = await [
      Permission.microphone,
      Permission.bluetoothConnect,
      Permission.bluetoothScan,
    ].request();

    final denied = statuses.entries
        .where((entry) => !entry.value.isGranted)
        .map((entry) => entry.key.toString())
        .toList();

    if (!mounted) return;

    if (denied.isEmpty) {
      context.go('/home');
    } else {
      setState(() {
        _requesting = false;
        _denialMessage =
            'EchoEcho-T needs microphone and Bluetooth access to translate '
            'your conversations. Denied: ${denied.join(', ')}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.translate, size: 72),
              const SizedBox(height: 16),
              const Text(
                'EchoEcho-T',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Real-time offline translation through your Bluetooth earbuds.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              if (_denialMessage != null) ...[
                Text(
                  _denialMessage!,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
                const SizedBox(height: 16),
              ],
              FilledButton(
                onPressed: _requesting ? null : _requestPermissions,
                child: _requesting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Grant permissions & continue'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
