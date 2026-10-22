import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/core/api/api_client.dart';
import 'package:mobile/core/api/models.dart';
import 'package:mobile/features/analysis/analysis_result_screen.dart';

const DiseaseInfo blastDisease = DiseaseInfo(
  code: 'padi-blast',
  name: 'Rice Blast',
  nameLocal: 'Blas',
  symptoms: 'Bercak berbentuk belah ketupat dengan pusat abu-abu.',
  prevention: 'Gunakan varietas tahan dan hindari nitrogen berlebihan.',
  management: 'Konsultasikan pengendalian dengan penyuluh pertanian.',
  source: 'IRRI Rice Knowledge Bank.',
);

const PredictionResult blastResult = PredictionResult(
  analysisId: 'abc',
  cropName: 'padi',
  label: 'Rice Blast',
  explanation: 'Prediksi: Blas (Blast).',
  confidence: 0.99,
  disease: blastDisease,
  modelVersion: 'rice-mobilenetv2-v1',
);

Widget buildScreen({ApiClient? api, PredictionResult result = blastResult}) {
  return MaterialApp(
    home: AnalysisResultScreen(
      imageBytes: null,
      result: result,
      onDone: () {},
      api: api,
    ),
  );
}

ApiClient buildApi() {
  return ApiClient(
    baseUrl: 'http://test/api/v1',
    httpClient: MockClient((http.Request request) async {
      const Map<String, String> headers = <String, String>{
        'content-type': 'application/json',
      };

      if (request.url.path == '/api/v1/diseases/') {
        return http.Response(
          jsonEncode(<Map<String, dynamic>>[
            <String, dynamic>{
              'code': 'padi-blast',
              'name': 'Rice Blast',
              'name_local': 'Blas',
              'symptoms': '',
              'prevention': '',
              'management': '',
              'source': '',
            },
            <String, dynamic>{
              'code': 'padi-bacterial-blight',
              'name': 'Bacterial Leaf Blight',
              'name_local': 'Hawar Daun Bakteri',
              'symptoms': '',
              'prevention': '',
              'management': '',
              'source': '',
            },
          ]),
          200,
          headers: headers,
        );
      }

      if (request.url.path == '/api/v1/analyses/abc/feedback/') {
        final Map<String, dynamic> body =
            jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['is_correct'], false);
        return http.Response(
          jsonEncode(<String, dynamic>{
            'id': 'feedback-1',
            'is_correct': false,
            'suggested_disease': body['suggested_disease'],
            'note': body['note'] ?? '',
            'created_at': '2026-10-22T00:10:39.500207+08:00',
            'updated_at': '2026-10-22T00:10:39.500207+08:00',
          }),
          201,
          headers: headers,
        );
      }

      return http.Response('{}', 404, headers: headers);
    }),
  );
}

void main() {
  testWidgets('result screen shows guidance and a clear warning',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 1400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(buildScreen());
    await tester.pumpAndSettle();

    expect(find.text('Rice Blast'), findsWidgets);
    expect(find.text('Model confidence: 99%'), findsOneWidget);
    expect(
      find.textContaining('High confidence does not guarantee correctness'),
      findsOneWidget,
    );
    expect(find.text('Symptoms to check'), findsOneWidget);
    expect(find.text(blastDisease.symptoms), findsOneWidget);
    expect(find.text('Prevention'), findsOneWidget);
    expect(find.text(blastDisease.prevention), findsOneWidget);
    expect(find.text('What to do next'), findsOneWidget);
    expect(find.text(blastDisease.management), findsOneWidget);
    expect(find.textContaining('Source: IRRI Rice Knowledge Bank'), findsOneWidget);
  });

  testWidgets('can report an incorrect result', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 1400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(buildScreen(api: buildApi()));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Report incorrect result'));
    await tester.tap(find.text('Report incorrect result'));
    await tester.pumpAndSettle();

    expect(find.text('Report this result'), findsOneWidget);

    await tester.tap(find.text('Incorrect'));
    await tester.pumpAndSettle();

    expect(find.text('What do you think it is? (optional)'), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'Lesi memanjang.');
    await tester.ensureVisible(find.text('Submit report'));
    await tester.tap(find.text('Submit report'));
    await tester.pumpAndSettle();

    expect(
      find.textContaining('You marked this prediction as incorrect'),
      findsOneWidget,
    );
    expect(find.text('Thank you. Your report was saved.'), findsOneWidget);
  });

  testWidgets('healthy result explains that no supported disease was found',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 1400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    const PredictionResult healthy = PredictionResult(
      analysisId: 'abc',
      cropName: 'padi',
      label: 'Healthy Rice Leaf',
      explanation: 'Prediksi: Daun Sehat.',
      confidence: 0.97,
      disease: DiseaseInfo(
        code: 'padi-sehat',
        name: 'Healthy Rice Leaf',
        symptoms: 'Daun berwarna hijau merata.',
        prevention: 'Pemupukan berimbang.',
        management: 'Pantau tanaman secara berkala.',
        source: 'Dataset padi.',
      ),
    );

    await tester.pumpWidget(buildScreen(result: healthy));
    await tester.pumpAndSettle();

    expect(find.textContaining('did not detect one of the four supported'),
        findsOneWidget);
    expect(find.text('What a healthy leaf looks like'), findsOneWidget);
    expect(find.text('Daun berwarna hijau merata.'), findsOneWidget);
  });
}
