import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../models/latency_metrics.dart';
import '../providers/pipeline_state_notifier.dart';
import '../providers/settings_provider.dart';
import '../services/echoecho_api.g.dart';
import '../widgets/bluetooth_device_picker.dart';
import '../widgets/latency_display.dart';
import '../widgets/status_indicator.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pipeline = ref.watch(pipelineStateProvider);
    final languagePair = ref.watch(settingsProvider);
    final isRunning = pipeline.stage != PipelineStage.idle;

    return Scaffold(
      appBar: AppBar(
        title: const Text('EchoEcho-T'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              StatusIndicator(stage: pipeline.stage),
              const SizedBox(height: 16),
              const BluetoothDevicePicker(),
              const SizedBox(height: 16),
              Text(
                '${languagePair.sourceCode.toUpperCase()} → '
                '${languagePair.targetCode.toUpperCase()}',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const Spacer(),
              const LatencyDisplay(latency: LatencySnapshot()),
              const SizedBox(height: 24),
              FilledButton.icon(
                icon: Icon(isRunning ? Icons.stop : Icons.mic),
                label: Text(isRunning ? 'Stop' : 'Start conversation'),
                onPressed: () {
                  final notifier = ref.read(pipelineStateProvider.notifier);
                  if (isRunning) {
                    notifier.stop();
                  } else {
                    notifier.start(
                      languagePair.sourceCode,
                      languagePair.targetCode,
                    );
                  }
                },
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
