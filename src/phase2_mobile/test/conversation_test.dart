import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:phase2_mobile/models/language_config.dart';
import 'package:phase2_mobile/screens/home_screen.dart';
import 'package:phase2_mobile/services/speech_service.dart';
import 'package:phase2_mobile/services/translation_service.dart';

class FakeTranslator extends TranslationService {
  final result = Completer<String>();
  @override
  Future<String> translate({
    required String endpoint,
    required String model,
    required String text,
    required LanguagePairConfig languages,
  }) => result.future;
}

class FakeSpeech extends SpeechService {
  @override
  Future<void> stop() async {}
}

void main() {
  testWidgets('translation becomes a conversation card and can be cleared', (
    tester,
  ) async {
    final translator = FakeTranslator();
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          translationService: translator,
          speechService: FakeSpeech(),
        ),
      ),
    );
    await tester.enterText(find.byType(TextField).first, 'Hello');
    await tester.tap(find.widgetWithText(FilledButton, 'Translate'));
    await tester.pump();
    expect(find.text('Translating…'), findsOneWidget);
    translator.result.complete('வணக்கம்');
    await tester.pumpAndSettle();
    await tester.drag(find.byType(ListView), const Offset(0, -450));
    await tester.pumpAndSettle();
    expect(find.text('வணக்கம்'), findsOneWidget);
    await tester.ensureVisible(find.text('Clear'));
    await tester.tap(find.text('Clear'));
    await tester.pumpAndSettle();
    expect(find.text('வணக்கம்'), findsNothing);
  });
  testWidgets('cancel ignores late translation results', (tester) async {
    final translator = FakeTranslator();
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          translationService: translator,
          speechService: FakeSpeech(),
        ),
      ),
    );
    await tester.enterText(find.byType(TextField).first, 'Hello');
    await tester.tap(find.widgetWithText(FilledButton, 'Translate'));
    await tester.pump();
    await tester.ensureVisible(find.text('Cancel'));
    await tester.tap(find.text('Cancel'));
    translator.result.complete('stale translation');
    await tester.pumpAndSettle();
    expect(find.text('stale translation'), findsNothing);
    expect(find.text('Hello'), findsOneWidget);
  });
}
