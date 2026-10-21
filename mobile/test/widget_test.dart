import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/app.dart';
import 'package:mobile/core/api/api_client.dart';
import 'package:mobile/core/api/models.dart';
import 'package:mobile/core/session/session_controller.dart';
import 'package:mobile/core/session/token_store.dart';

ApiClient buildApi({
  List<Map<String, dynamic>> crops = const <Map<String, dynamic>>[],
  List<Map<String, dynamic>> analyses = const <Map<String, dynamic>>[],
  Map<String, dynamic> user = const <String, dynamic>{
    'id': 1,
    'username': 'petani',
  },
}) {
  final MockClient client = MockClient((http.Request request) async {
    final String path = request.url.path;
    final Map<String, String> headers = <String, String>{
      'content-type': 'application/json',
    };

    if (path.endsWith('/crops/')) {
      return http.Response(jsonEncode(crops), 200, headers: headers);
    }
    if (path.endsWith('/analyses/') && request.method == 'GET') {
      return http.Response(jsonEncode(analyses), 200, headers: headers);
    }
    if (path.endsWith('/auth/me/')) {
      return http.Response(jsonEncode(user), 200, headers: headers);
    }

    return http.Response(
      jsonEncode(<String, dynamic>{
        'error': <String, dynamic>{
          'code': 'not_found',
          'message': 'Not found.',
        },
      }),
      404,
      headers: headers,
    );
  });

  return ApiClient(httpClient: client, baseUrl: 'http://test/api/v1');
}

SessionController buildSession({
  ApiClient? api,
  String? token = 'test-token',
  AuthUser? user,
}) {
  final ApiClient client = api ?? buildApi();
  return SessionController.authenticated(
    client,
    MemoryTokenStore(token),
    user ??
        const AuthUser(id: 1, username: 'petani', displayName: 'Petani'),
    token: token,
  );
}

void main() {
  testWidgets('shows the sign-in screen when there is no saved token',
      (WidgetTester tester) async {
    final SessionController session = SessionController(
      api: buildApi(),
      tokenStore: MemoryTokenStore(),
    );

    await tester.pumpWidget(AgroniaApp(session: session));
    await tester.pumpAndSettle();

    expect(find.text('Sign in'), findsWidgets);
    expect(find.text('Welcome'), findsNothing);
  });

  testWidgets('starts on home and exposes the four main destinations',
      (WidgetTester tester) async {
    await tester.pumpWidget(AgroniaApp(session: buildSession()));
    await tester.pumpAndSettle();

    expect(find.text('Agronia'), findsOneWidget);
    expect(find.text('Analyze crop image'), findsOneWidget);
    expect(find.text('Analysis history'), findsOneWidget);

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
    await tester.pumpWidget(AgroniaApp(session: buildSession()));
    await tester.pumpAndSettle();

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

    await tester.pumpWidget(AgroniaApp(session: buildSession()));
    await tester.pumpAndSettle();

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

  testWidgets('shows completed history records from the API',
      (WidgetTester tester) async {
    final ApiClient api = buildApi(
      analyses: <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'abc',
          'status': 'completed',
          'crop': 'padi',
          'predicted_disease': 'blast',
          'confidence': 0.91,
          'model_version': 'v1',
          'message': 'Perkiraan awal.',
          'image_url': '/api/v1/analyses/abc/image/',
          'prediction': <String, dynamic>{
            'class_id': 'blast',
            'label': 'Blast Padi',
            'confidence': 0.91,
            'model_version': 'v1',
            'is_confident': true,
          },
          'created_at': '2026-10-22T00:10:39.500207+08:00',
        },
      ],
    );

    await tester.pumpWidget(
      AgroniaApp(session: buildSession(api: api)),
    );
    await tester.pumpAndSettle();

    await tester.tap(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('History'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Blast Padi'), findsOneWidget);
  });

  testWidgets('failed analyses are never shown as a diagnosis',
      (WidgetTester tester) async {
    final ApiClient api = buildApi(
      analyses: <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'abc',
          'status': 'failed',
          'crop': null,
          'predicted_disease': null,
          'confidence': null,
          'model_version': '',
          'message': 'Model AI belum tersedia.',
          'image_url': '/api/v1/analyses/abc/image/',
          'prediction': null,
          'created_at': '2026-10-22T00:10:39.500207+08:00',
        },
      ],
    );

    await tester.pumpWidget(
      AgroniaApp(session: buildSession(api: api)),
    );
    await tester.pumpAndSettle();

    await tester.tap(
      find.descendant(
        of: find.byType(NavigationBar),
        matching: find.text('History'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Analysis failed'), findsOneWidget);

    await tester.tap(find.text('Analysis failed'));
    await tester.pumpAndSettle();

    expect(find.text('Analysis not completed'), findsOneWidget);
    expect(find.text('No diagnosis was produced for this photo.'),
        findsOneWidget);
  });
}
