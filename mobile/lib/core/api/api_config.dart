abstract final class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000/api/v1',
  );

  static String get serverRoot {
    return baseUrl.replaceFirst(RegExp(r'/api/v1/?$'), '');
  }

  static Uri resolve(String path) {
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return Uri.parse(path);
    }
    final String normalized = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$serverRoot$normalized');
  }
}
