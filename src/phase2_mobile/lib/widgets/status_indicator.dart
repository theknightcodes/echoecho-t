import 'package:flutter/material.dart';

import '../services/echoecho_api.g.dart';

class StatusIndicator extends StatelessWidget {
  const StatusIndicator({super.key, required this.stage});

  final PipelineStage stage;

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (stage) {
      PipelineStage.idle => ('Idle', Colors.grey),
      PipelineStage.listening => ('Listening', Colors.blue),
      PipelineStage.processing => ('Processing', Colors.orange),
      PipelineStage.speaking => ('Speaking', Colors.green),
      PipelineStage.error => ('Error', Colors.red),
    };

    return Chip(
      avatar: CircleAvatar(backgroundColor: color),
      label: Text(label),
    );
  }
}
