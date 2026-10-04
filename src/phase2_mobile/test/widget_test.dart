import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:phase2_mobile/app.dart';

void main() {
  testWidgets('App boots to the onboarding screen', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: EchoEchoApp()));
    await tester.pumpAndSettle();

    expect(find.text('EthirOli'), findsOneWidget);
    expect(find.text('Get started'), findsOneWidget);
  });
}
