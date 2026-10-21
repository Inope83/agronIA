import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app.dart';

void main() {
  testWidgets('starts on home and exposes the four main destinations',
      (WidgetTester tester) async {
    await tester.pumpWidget(const AgroniaApp());

    expect(find.text('Agronia'), findsOneWidget);
    expect(find.text('Analyze crop image'), findsOneWidget);
    expect(find.text('No analyses yet. Submitted images and results will appear here.'),
        findsOneWidget);

    expect(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('Analyze'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('History'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('Learn'),
      ),
      findsOneWidget,
    );
  });

  testWidgets('navigates to History and Analyze', (WidgetTester tester) async {
    await tester.pumpWidget(const AgroniaApp());

    await tester.tap(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('History'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No analyses yet'), findsOneWidget);

    await tester.tap(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('Analyze'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Analyze a crop image'), findsOneWidget);
  });

  testWidgets('requires an image before analysis', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 1200));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const AgroniaApp());

    await tester.tap(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('Analyze'),
      ),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Analyze image'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Analyze image'));
    await tester.pump();

    expect(find.text('Select a photo of the affected crop first.'),
        findsOneWidget);
  });
}
