import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/core/api/api_client.dart';
import 'package:mobile/core/api/api_exception.dart';
import 'package:mobile/core/api/models.dart';

void main() {
  test('login stores the token and parses the user', () async {
    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      httpClient: MockClient((http.Request request) async {
        expect(request.url.path, '/api/v1/auth/login/');
        expect(request.headers['content-type'], startsWith('application/json'));
        return http.Response(
          jsonEncode(<String, dynamic>{
            'token': 'abc123',
            'user': <String, dynamic>{
              'id': 7,
              'username': 'petani',
              'email': 'petani@example.com',
              'profile': <String, dynamic>{'display_name': 'Petani'},
            },
          }),
          200,
          headers: <String, String>{'content-type': 'application/json'},
        );
      }),
    );

    final AuthSession session = await api.login(
      username: 'petani',
      password: 'RahasiaKuat123',
    );

    expect(session.token, 'abc123');
    expect(session.user.id, 7);
    expect(session.user.email, 'petani@example.com');
    expect(session.user.label, 'Petani');
    expect(api.token, 'abc123');
  });

  test('backend error codes are preserved', () async {
    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      httpClient: MockClient((http.Request request) async {
        return http.Response(
          jsonEncode(<String, dynamic>{
            'error': <String, dynamic>{
              'code': 'invalid_credentials',
              'message': 'Username atau password salah.',
            },
          }),
          401,
          headers: <String, String>{'content-type': 'application/json'},
        );
      }),
    );

    expect(
      () => api.login(username: 'a', password: 'b'),
      throwsA(
        isA<ApiException>()
            .having((ApiException error) => error.code, 'code',
                'invalid_credentials')
            .having((ApiException error) => error.statusCode, 'status', 401)
            .having((ApiException error) => error.isUnauthorized,
                'isUnauthorized', true),
      ),
    );
  });

  test('network failures become a clear ApiException', () async {
    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      httpClient: MockClient((http.Request request) async {
        throw http.ClientException('connection refused');
      }),
    );

    expect(
      () => api.fetchCrops(),
      throwsA(
        isA<ApiException>().having(
          (ApiException error) => error.code,
          'code',
          'network_error',
        ),
      ),
    );
  });

  test('timeouts become a clear ApiException', () async {
    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      requestTimeout: const Duration(milliseconds: 20),
      httpClient: MockClient((http.Request request) async {
        await Future<void>.delayed(const Duration(milliseconds: 200));
        return http.Response('[]', 200);
      }),
    );

    expect(
      () => api.fetchCrops(),
      throwsA(
        isA<ApiException>().having(
          (ApiException error) => error.code,
          'code',
          'network_timeout',
        ),
      ),
    );
  });

  test('createAnalysis sends the image, crop, and auth token', () async {
    late String requestBody;
    late String? authorization;

    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      httpClient: MockClient((http.Request request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/api/v1/analyses/');
        expect(
          request.headers['content-type'],
          startsWith('multipart/form-data'),
        );
        authorization = request.headers['authorization'];
        requestBody = utf8.decode(request.bodyBytes, allowMalformed: true);

        return http.Response(
          jsonEncode(<String, dynamic>{
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
          }),
          201,
          headers: <String, String>{'content-type': 'application/json'},
        );
      }),
    );
    api.token = 'secret-token';

    final AnalysisRecord record = await api.createAnalysis(
      bytes: Uint8List.fromList(<int>[1, 2, 3, 4]),
      filename: 'padi.png',
      crop: 'padi',
    );

    expect(authorization, 'Token secret-token');
    expect(requestBody, contains('name="image"'));
    expect(requestBody, contains('filename="padi.png"'));
    expect(requestBody, contains('name="crop"'));
    expect(requestBody, contains('padi'));

    expect(record.hasPrediction, true);
    expect(record.prediction!.label, 'Blast Padi');
    expect(record.confidence, 0.91);
  });

  test('fetchAnalyses parses failed records without inventing a label',
      () async {
    final ApiClient api = ApiClient(
      baseUrl: 'http://test/api/v1',
      httpClient: MockClient((http.Request request) async {
        return http.Response(
          jsonEncode(<Map<String, dynamic>>[
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
          ]),
          200,
          headers: <String, String>{'content-type': 'application/json'},
        );
      }),
    );

    final List<AnalysisRecord> records = await api.fetchAnalyses();

    expect(records, hasLength(1));
    expect(records.first.isFailed, true);
    expect(records.first.hasPrediction, false);
    expect(records.first.prediction, isNull);
    expect(records.first.label, 'Analysis failed');
  });
}
