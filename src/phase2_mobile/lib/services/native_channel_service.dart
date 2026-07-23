import 'echoecho_api.g.dart';

/// Dart-side wrapper over the Pigeon-generated host API stub.
///
/// Milestone 1 only wires the channel; the Kotlin side has no pipeline
/// implementation yet, so calls are stubs until Milestone 2+.
class NativeChannelService {
  NativeChannelService({EchoEchoHostApi? hostApi})
      : _hostApi = hostApi ?? EchoEchoHostApi();

  final EchoEchoHostApi _hostApi;

  Future<void> startPipeline({
    required String sourceLanguage,
    required String targetLanguage,
  }) {
    return _hostApi.startPipeline(sourceLanguage, targetLanguage);
  }

  Future<void> stopPipeline() {
    return _hostApi.stopPipeline();
  }
}
