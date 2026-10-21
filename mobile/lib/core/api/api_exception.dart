class ApiException implements Exception {
  const ApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.details,
  });

  final String code;
  final String message;
  final int? statusCode;
  final Map<String, dynamic>? details;

  bool get isUnauthorized => statusCode == 401;

  bool get isNetworkFailure =>
      code == 'network_error' || code == 'network_timeout';

  @override
  String toString() => 'ApiException($code, $statusCode): $message';
}
