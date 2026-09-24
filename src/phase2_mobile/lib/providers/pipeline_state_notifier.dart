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

  bool _busy = false;

  Future<void> start(String sourceLanguage, String targetLanguage) async {
    if (_busy ||
        state.stage == PipelineStage.listening ||
        state.stage == PipelineStage.processing ||
        state.stage == PipelineStage.speaking) {
      return;
    }
    _busy = true;
    try {
      await _nativeChannel.startPipeline(
        sourceLanguage: sourceLanguage,
        targetLanguage: targetLanguage,
      );
      if (mounted) state = const PipelineStatus(stage: PipelineStage.listening);
    } catch (_) {
      if (mounted) {
        state = const PipelineStatus(
          stage: PipelineStage.error,
          message:
              'Translation could not start. The native translation engine '
              'is not available in this build.',
        );
      }
    } finally {
      _busy = false;
    }
  }

  Future<void> stop() async {
    if (_busy) return;
    _busy = true;
    try {
      await _nativeChannel.stopPipeline();
      if (mounted) state = const PipelineStatus();
    } catch (_) {
      if (mounted) {
        state = const PipelineStatus(
          stage: PipelineStage.error,
          message: 'Translation could not stop. Close the app and try again.',
        );
      }
    } finally {
      _busy = false;
    }
  }

  void onStatusUpdate(StatusUpdate status) {
    if (mounted) {
      state = PipelineStatus(stage: status.stage, message: status.message);
    }
  }
}

final pipelineStateProvider =
    StateNotifierProvider<PipelineStateNotifier, PipelineStatus>((ref) {
      return PipelineStateNotifier(ref.watch(nativeChannelServiceProvider));
    });
