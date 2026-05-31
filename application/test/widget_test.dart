import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sign_language_translator/app/sign_language_app.dart';

void main() {
  testWidgets('Sign language app launches splash screen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const ProviderScope(child: SignLanguageApp()),
    );

    expect(find.text('Sign Language Translator'), findsOneWidget);
    expect(find.text('AI powered'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
  });
}
