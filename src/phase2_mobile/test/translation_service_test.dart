import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:phase2_mobile/models/language_config.dart';
import 'package:phase2_mobile/services/translation_service.dart';

void main() {
  late HttpServer server;
  late String endpoint;
  setUp(() async {
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    endpoint = 'http://127.0.0.1:${server.port}';
  });
  tearDown(() => server.close(force: true));

  Future<String> translate({
    String text = 'Hello',
    String model = 'test',
    LanguagePairConfig languages = const LanguagePairConfig(),
  }) => TranslationService().translate(
    endpoint: endpoint,
    model: model,
    text: text,
    languages: languages,
  );

  test('sends correct language instructions and preserves Unicode', () async {
    server.listen((request) async {
      expect(request.uri.path, '/api/chat');
      final body = jsonDecode(await utf8.decoder.bind(request).join());
      expect(body['stream'], false);
      expect(body['messages'][0]['content'], contains('English to Tamil'));
      expect(body['messages'][1]['content'], 'Hello');
      request.response.write(
        jsonEncode({
          'message': {'content': 'வணக்கம்'},
          'done': true,
        }),
      );
      await request.response.close();
    });
    expect(await translate(), 'வணக்கம்');
  });

  test('uses the selected non-Tamil language pair in the prompt', () async {
    server.listen((request) async {
      final body = jsonDecode(await utf8.decoder.bind(request).join());
      expect(body['messages'][0]['content'], contains('Hindi to Spanish'));
      request.response.write(
        jsonEncode({
          'message': {'content': 'Buenos días'},
          'done': true,
        }),
      );
      await request.response.close();
    });
    expect(
      await translate(
        text: 'सुप्रभात',
        languages: const LanguagePairConfig(sourceCode: 'hi', targetCode: 'es'),
      ),
      'Buenos días',
    );
  });

  test('rejects missing model, empty text and same-language pair', () async {
    await expectLater(translate(model: ''), throwsFormatException);
    await expectLater(translate(text: '  '), throwsFormatException);
    await expectLater(
      translate(languages: const LanguagePairConfig(targetCode: 'en')),
      throwsFormatException,
    );
  });

  test('server failures are actionable', () async {
    server.listen((request) async {
      request.response.statusCode = 404;
      await request.response.close();
    });
    await expectLater(translate(), throwsA(isA<HttpException>()));
  });

  test('rejects empty and truncated model output', () async {
    server.listen((request) async {
      request.response.write(
        jsonEncode({
          'message': {'content': 'partial'},
          'done_reason': 'length',
        }),
      );
      await request.response.close();
    });
    await expectLater(translate(), throwsFormatException);
  });
}
