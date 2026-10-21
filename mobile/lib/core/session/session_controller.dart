import 'package:flutter/foundation.dart';

import '../api/api_client.dart';
import '../api/api_exception.dart';
import '../api/models.dart';
import 'token_store.dart';

class SessionController extends ChangeNotifier {
  SessionController({required this.api, required this.tokenStore});

  SessionController.authenticated(
    this.api,
    this.tokenStore,
    this._user, {
    String? token,
  }) : _isInitializing = false {
    if (token != null) {
      api.token = token;
    }
  }

  final ApiClient api;
  final TokenStore tokenStore;

  AuthUser? _user;
  bool _isInitializing = true;
  String? _initializationError;

  AuthUser? get user => _user;
  bool get isAuthenticated => _user != null;
  bool get isInitializing => _isInitializing;
  String? get initializationError => _initializationError;

  Future<void> initialize() async {
    _isInitializing = true;
    _initializationError = null;

    try {
      String? token;
      try {
        token = await tokenStore.read();
      } on Exception {
        token = null;
      }
      if (token != null && token.isNotEmpty) {
        api.token = token;
        try {
          _user = await api.me();
        } on ApiException catch (error) {
          if (error.isUnauthorized) {
            api.token = null;
            await tokenStore.clear();
          } else {
            _initializationError = error.message;
          }
        }
      }
    } finally {
      _isInitializing = false;
      notifyListeners();
    }
  }

  Future<void> login({
    required String username,
    required String password,
  }) async {
    final AuthSession session = await api.login(
      username: username,
      password: password,
    );
    await _saveToken(session.token);
    _user = session.user;
    _initializationError = null;
    notifyListeners();
  }

  Future<void> register({
    required String username,
    required String email,
    required String password,
    required String passwordConfirm,
  }) async {
    final AuthSession session = await api.register(
      username: username,
      email: email,
      password: password,
      passwordConfirm: passwordConfirm,
    );
    await _saveToken(session.token);
    _user = session.user;
    _initializationError = null;
    notifyListeners();
  }

  Future<void> logout() async {
    try {
      await api.logout();
    } on ApiException {
      // Token lokal tetap dihapus meski server tidak dapat dijangkau.
    } finally {
      api.token = null;
      await _clearToken();
      _user = null;
      notifyListeners();
    }
  }

  Future<void> _saveToken(String token) async {
    try {
      await tokenStore.write(token);
    } on Exception {
      return;
    }
  }

  Future<void> _clearToken() async {
    try {
      await tokenStore.clear();
    } on Exception {
      return;
    }
  }
}
