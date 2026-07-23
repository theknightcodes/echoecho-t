import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/pipeline_status.dart';
import '../services/echoecho_api.g.dart';
import '../services/native_channel_service.dart';

final nativeChannelServiceProvider = Provider<NativeChannelService>((ref) {
  return NativeChannelService();
});

class PipelineStateNotifier extends StateNotifier<PipelineStatus> {
  PipelineStateNotifier(this._nativeChannel) : super(const PipelineStatus());

  final NativeChannelService _nativeChannel;

  Future<void> start(String sourceLanguage, String targetLanguage) async {
    state = state.copyWith(stage: PipelineStage.listening);
    await _nativeChannel.startPipeline(
      sourceLanguage: sourceLanguage,
      targetLanguage: targetLanguage,
    );
  }

  Future<void> stop() async {
    await _nativeChannel.stopPipeline();
    state = state.copyWith(stage: PipelineStage.idle);
  }

  void onStatusUpdate(StatusUpdate status) {
    state = PipelineStatus(stage: status.stage, message: status.message);
  }
}

final pipelineStateProvider =
    StateNotifierProvider<PipelineStateNotifier, PipelineStatus>((ref) {
  return PipelineStateNotifier(ref.watch(nativeChannelServiceProvider));
});
