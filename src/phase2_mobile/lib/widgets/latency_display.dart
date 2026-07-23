import 'package:flutter/material.dart';

import '../models/latency_metrics.dart';

class LatencyDisplay extends StatelessWidget {
  const LatencyDisplay({super.key, required this.latency});

  final LatencySnapshot latency;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _stat('VAD', latency.vadMs),
        _stat('STT', latency.sttMs),
        _stat('MT', latency.translationMs),
        _stat('TTS', latency.ttsMs),
        _stat('Total', latency.totalMs),
      ],
    );
  }

  Widget _stat(String label, double ms) {
    return Column(
      children: [
        Text('${ms.toStringAsFixed(0)}ms',
            style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
