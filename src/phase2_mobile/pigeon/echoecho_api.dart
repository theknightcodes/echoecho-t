import 'package:pigeon/pigeon.dart';

@ConfigurePigeon(PigeonOptions(
  dartOut: 'lib/services/echoecho_api.g.dart',
  kotlinOut:
      'android/app/src/main/kotlin/com/echoecho/phase2_mobile/platform/EchoEchoApi.g.kt',
  kotlinOptions: KotlinOptions(package: 'com.echoecho.phase2_mobile.platform'),
))

/// Pipeline lifecycle stages surfaced to the UI.
enum PipelineStage {
  idle,
  listening,
  processing,
  speaking,
  error,
}

class StatusUpdate {
  StatusUpdate({required this.stage, this.message});

  final PipelineStage stage;
  final String? message;
}

class LatencyMetrics {
  LatencyMetrics({
    required this.vadMs,
    required this.sttMs,
    required this.translationMs,
    required this.ttsMs,
    required this.totalMs,
  });

  final double vadMs;
  final double sttMs;
  final double translationMs;
  final double ttsMs;
  final double totalMs;
}

/// Dart -> Kotlin: commands the Flutter UI sends to the native pipeline.
@HostApi()
abstract class EchoEchoHostApi {
  void startPipeline(String sourceLanguage, String targetLanguage);

  void stopPipeline();
}

/// Kotlin -> Dart: events the native pipeline pushes to the Flutter UI.
@FlutterApi()
abstract class EchoEchoFlutterApi {
  void onStatusUpdate(StatusUpdate status);

  void onLatencyUpdate(LatencyMetrics metrics);
}
