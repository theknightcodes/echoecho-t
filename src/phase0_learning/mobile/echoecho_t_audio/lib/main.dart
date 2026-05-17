import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const ProviderScope(child: EchoEchoAudioApp()));
}

class EchoEchoAudioApp extends StatelessWidget {
  const EchoEchoAudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EchoEcho-T Audio',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
