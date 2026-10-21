import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import 'api_config.dart';
import 'api_exception.dart';
import 'models.dart';

class ApiClient {
  ApiClient({
    http.Client? httpClient,
    String? baseUrl,
    this.requestTimeout = const Duration(seconds: 60),
  })  : _http = httpClient ?? http.Client(),
        baseUrl = baseUrl ?? ApiConfig.baseUrl;

  final http.Client _http;
  final String baseUrl;
  final Duration requestTimeout;

  String? token;

  Map<String, String> get _headers {
    final Map<String, String> headers = <String, String>{
      'Accept': 'application/json',
    };
    if (token != null && token!.isNotEmpty) {
      headers['Authorization'] = 'Token $token';
    }
    return headers;
  }

  Map<String, String> get _jsonHeaders => <String, String>{
        ..._headers,
        'Content-Type': 'application/json',
      };

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<AuthSession> login({
    required String username,
    required String password,
  }) async {
    final http.Response response = await _guard(
      () => _http.post(
        _uri('/auth/login/'),
        headers: _jsonHeaders,
        body: jsonEncode(<String, String>{
          'username': username,
          'password': password,
        }),
      ),
    );

    if (response.statusCode != 200) {
      throw _exceptionFrom(response);
    }

    return _parseAuthSession(response);
  }

  Future<AuthSession> register({
    required String username,
    required String email,
    required String password,
    required String passwordConfirm,
  }) async {
    final http.Response response = await _guard(
      () => _http.post(
        _uri('/auth/register/'),
        headers: _jsonHeaders,
        body: jsonEncode(<String, String>{
          'username': username,
          'email': email,
          'password': password,
          'password_confirm': passwordConfirm,
        }),
      ),
    );

    if (response.statusCode != 201) {
      throw _exceptionFrom(response);
    }

    return _parseAuthSession(response);
  }

  Future<AuthUser> me() async {
    final http.Response response = await _guard(
      () => _http.get(_uri('/auth/me/'), headers: _headers),
    );

    if (response.statusCode != 200) {
      throw _exceptionFrom(response);
    }

    return AuthUser.fromJson(_decodeObject(response));
  }

  Future<void> logout() async {
    final http.Response response = await _guard(
      () => _http.post(_uri('/auth/logout/'), headers: _headers),
    );

    if (response.statusCode != 204 && response.statusCode != 401) {
      throw _exceptionFrom(response);
    }
  }

  Future<List<CropOption>> fetchCrops() async {
    final http.Response response = await _guard(
      () => _http.get(_uri('/crops/'), headers: _headers),
    );

    if (response.statusCode != 200) {
      throw _exceptionFrom(response);
    }

    final Object? decoded = _tryDecode(response);
    if (decoded is! List) {
      throw const ApiException(
        code: 'invalid_response',
        message: 'Daftar tanaman dari server tidak valid.',
      );
    }

    return decoded
        .whereType<Map<String, dynamic>>()
        .map(CropOption.fromJson)
        .where((CropOption crop) => crop.code.isNotEmpty)
        .toList();
  }

  Future<List<AnalysisRecord>> fetchAnalyses() async {
    final http.Response response = await _guard(
      () => _http.get(_uri('/analyses/'), headers: _headers),
    );

    if (response.statusCode != 200) {
      throw _exceptionFrom(response);
    }

    final Object? decoded = _tryDecode(response);
    if (decoded is! List) {
      throw const ApiException(
        code: 'invalid_response',
        message: 'Riwayat analisis dari server tidak valid.',
      );
    }

    return decoded
        .whereType<Map<String, dynamic>>()
        .map(AnalysisRecord.fromJson)
        .toList();
  }

  Future<AnalysisRecord> createAnalysis({
    required Uint8List bytes,
    required String filename,
    String? crop,
  }) async {
    final http.MultipartRequest request = http.MultipartRequest(
      'POST',
      _uri('/analyses/'),
    );
    request.headers.addAll(_headers);
    request.files.add(
      http.MultipartFile.fromBytes('image', bytes, filename: filename),
    );
    if (crop != null && crop.isNotEmpty) {
      request.fields['crop'] = crop;
    }

    final http.Response response = await _guard(() async {
      final http.StreamedResponse streamed = await _http.send(request);
      return http.Response.fromStream(streamed);
    });

    if (response.statusCode != 201) {
      throw _exceptionFrom(response);
    }

    return AnalysisRecord.fromJson(_decodeObject(response));
  }

  Future<Uint8List> fetchImage(String path) async {
    final http.Response response = await _guard(
      () => _http.get(ApiConfig.resolve(path), headers: _headers),
    );

    if (response.statusCode != 200) {
      throw _exceptionFrom(response);
    }

    return response.bodyBytes;
  }

  AuthSession _parseAuthSession(http.Response response) {
    final Map<String, dynamic> data = _decodeObject(response);
    final Object? token = data['token'];
    final Object? user = data['user'];

    if (token is! String || token.isEmpty || user is! Map<String, dynamic>) {
      throw const ApiException(
        code: 'invalid_response',
        message: 'Respons autentikasi dari server tidak valid.',
      );
    }

    this.token = token;
    return AuthSession(token: token, user: AuthUser.fromJson(user));
  }

  Map<String, dynamic> _decodeObject(http.Response response) {
    final Object? decoded = _tryDecode(response);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    throw const ApiException(
      code: 'invalid_response',
      message: 'Respons server tidak valid.',
    );
  }

  Object? _tryDecode(http.Response response) {
    if (response.body.isEmpty) {
      return null;
    }
    try {
      return jsonDecode(response.body);
    } on FormatException {
      return null;
    }
  }

  ApiException _exceptionFrom(http.Response response) {
    final Object? decoded = _tryDecode(response);

    if (decoded is Map<String, dynamic>) {
      final Object? error = decoded['error'];
      if (error is Map<String, dynamic>) {
        final Object? details = error['details'];
        return ApiException(
          code: error['code'] as String? ?? 'request_failed',
          message: error['message'] as String? ??
              'Permintaan tidak dapat diproses (${response.statusCode}).',
          statusCode: response.statusCode,
          details: details is Map<String, dynamic> ? details : null,
        );
      }
    }

    return ApiException(
      code: 'request_failed',
      message: 'Permintaan tidak dapat diproses (${response.statusCode}).',
      statusCode: response.statusCode,
    );
  }

  Future<http.Response> _guard(
    Future<http.Response> Function() action,
  ) async {
    try {
      return await action().timeout(requestTimeout);
    } on TimeoutException {
      throw const ApiException(
        code: 'network_timeout',
        message:
            'Server tidak merespons tepat waktu. Periksa koneksi lalu coba lagi.',
      );
    } on http.ClientException {
      throw ApiException(
        code: 'network_error',
        message:
            'Tidak dapat terhubung ke server di $baseUrl. '
            'Periksa koneksi dan alamat API.',
      );
    }
  }
}
