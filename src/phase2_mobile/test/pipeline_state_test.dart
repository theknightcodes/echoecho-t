import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:phase2_mobile/providers/pipeline_state_notifier.dart';
import 'package:phase2_mobile/models/pipeline_status.dart';
import 'package:phase2_mobile/services/echoecho_api.g.dart';
import 'package:phase2_mobile/services/native_channel_service.dart';

class FakeNative extends NativeChannelService {
  bool failStart = false;
  bool failStop = false;
  int starts = 0;
  Completer<void>? pending;

  @override
  Future<void> startPipeline({
    required String sourceLanguage,
    required String targetLanguage,
  }) async {
    starts++;
    if (failStart) throw StateError('unavailable');
    if (pending != null) await pending!.future;
  }

  @override
  Future<void> stopPipeline() async {
    if (failStop) throw StateError('stop failed');
  }
}

class TestPipelineNotifier extends PipelineStateNotifier {
  TestPipelineNotifier(super.nativeChannel);

  PipelineStatus get status => state;
}

void main() {
  test('failed startup reports error and allows retry', () async {
    final native = FakeNative()..failStart = true;
    final notifier = TestPipelineNotifier(native);
    addTearDown(notifier.dispose);
    await notifier.start('en', 'ta');
    expect(notifier.status.stage, PipelineStage.error);
    expect(notifier.status.message, isNotEmpty);
    native.failStart = false;
    await notifier.start('en', 'ta');
    expect(notifier.status.stage, PipelineStage.listening);
    expect(notifier.status.message, isNull);
    await notifier.stop();
    expect(notifier.status.stage, PipelineStage.idle);
  });

  test(
    'pending startup does not report listening or issue duplicate calls',
    () async {
      final native = FakeNative()..pending = Completer<void>();
      final notifier = TestPipelineNotifier(native);
      addTearDown(notifier.dispose);
      final first = notifier.start('en', 'de');
      await notifier.start('en', 'de');
      expect(native.starts, 1);
      expect(notifier.status.stage, PipelineStage.idle);
      native.pending!.complete();
      await first;
      expect(notifier.status.stage, PipelineStage.listening);
    },
  );

  test('failed stop is surfaced', () async {
    final native = FakeNative()..failStop = true;
    final notifier = TestPipelineNotifier(native);
    addTearDown(notifier.dispose);
    await notifier.start('en', 'de');
    await notifier.stop();
    expect(notifier.status.stage, PipelineStage.error);
  });

  test('completion after disposal does not write state', () async {
    final native = FakeNative()..pending = Completer<void>();
    final notifier = TestPipelineNotifier(native);
    final starting = notifier.start('en', 'de');
    notifier.dispose();
    native.pending!.complete();
    await starting;
  });
}
