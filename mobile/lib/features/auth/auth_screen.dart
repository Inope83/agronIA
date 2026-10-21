import 'package:flutter/material.dart';

import '../../core/api/api_exception.dart';
import '../../core/session/session_controller.dart';
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.session});

  final SessionController session;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _username = TextEditingController();
  final TextEditingController _email = TextEditingController();
  final TextEditingController _password = TextEditingController();
  final TextEditingController _passwordConfirm = TextEditingController();

  bool _isRegister = false;
  bool _isSubmitting = false;
  bool _obscurePassword = true;
  String? _error;

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _password.dispose();
    _passwordConfirm.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSubmitting = true;
      _error = null;
    });

    try {
      if (_isRegister) {
        await widget.session.register(
          username: _username.text.trim(),
          email: _email.text.trim(),
          password: _password.text,
          passwordConfirm: _passwordConfirm.text,
        );
      } else {
        await widget.session.login(
          username: _username.text.trim(),
          password: _password.text,
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = _messageFor(error));
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  String _messageFor(ApiException error) {
    final Map<String, dynamic>? details = error.details;
    if (details != null && details.isNotEmpty) {
      final List<String> messages = <String>[];
      for (final Object? value in details.values) {
        if (value is List) {
          messages.addAll(value.map((Object? item) => item.toString()));
        } else if (value != null) {
          messages.add(value.toString());
        }
      }
      if (messages.isNotEmpty) {
        return messages.join(' ');
      }
    }
    return error.message;
  }

  void _toggleMode() {
    setState(() {
      _isRegister = !_isRegister;
      _error = null;
      _password.clear();
      _passwordConfirm.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    Center(
                      child: Container(
                        width: 72,
                        height: 72,
                        decoration: const BoxDecoration(
                          color: AppColors.lightGreen,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.eco,
                          size: 36,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      'Agronia',
                      textAlign: TextAlign.center,
                      style: text.displaySmall,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _isRegister
                          ? 'Create an account to keep your analysis history private.'
                          : 'Sign in to analyze crops and review your history.',
                      textAlign: TextAlign.center,
                      style: text.bodyMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 26),
                    AppCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: <Widget>[
                          Text(
                            _isRegister ? 'Create account' : 'Sign in',
                            style: text.titleMedium,
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: _username,
                            enabled: !_isSubmitting,
                            textInputAction: TextInputAction.next,
                            autofillHints: const <String>[AutofillHints.username],
                            decoration: const InputDecoration(
                              labelText: 'Username',
                            ),
                            validator: (String? value) {
                              final String username = value?.trim() ?? '';
                              if (username.isEmpty) {
                                return 'Username wajib diisi.';
                              }
                              if (username.contains(' ')) {
                                return 'Username tidak boleh mengandung spasi.';
                              }
                              return null;
                            },
                          ),
                          if (_isRegister) ...<Widget>[
                            const SizedBox(height: 14),
                            TextFormField(
                              controller: _email,
                              enabled: !_isSubmitting,
                              keyboardType: TextInputType.emailAddress,
                              textInputAction: TextInputAction.next,
                              autofillHints: const <String>[
                                AutofillHints.email,
                              ],
                              decoration: const InputDecoration(
                                labelText: 'Email',
                              ),
                              validator: (String? value) {
                                final String email = value?.trim() ?? '';
                                if (email.isEmpty) {
                                  return 'Email wajib diisi.';
                                }
                                if (!email.contains('@') ||
                                    !email.contains('.')) {
                                  return 'Masukkan alamat email yang valid.';
                                }
                                return null;
                              },
                            ),
                          ],
                          const SizedBox(height: 14),
                          TextFormField(
                            controller: _password,
                            enabled: !_isSubmitting,
                            obscureText: _obscurePassword,
                            textInputAction: _isRegister
                                ? TextInputAction.next
                                : TextInputAction.done,
                            onFieldSubmitted: _isRegister
                                ? null
                                : (_) => _submit(),
                            decoration: InputDecoration(
                              labelText: 'Password',
                              suffixIcon: IconButton(
                                onPressed: () {
                                  setState(
                                    () => _obscurePassword = !_obscurePassword,
                                  );
                                },
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_outlined
                                      : Icons.visibility_off_outlined,
                                ),
                                tooltip: _obscurePassword
                                    ? 'Show password'
                                    : 'Hide password',
                              ),
                            ),
                            validator: (String? value) {
                              if ((value ?? '').length < 8) {
                                return 'Password minimal 8 karakter.';
                              }
                              return null;
                            },
                          ),
                          if (_isRegister) ...<Widget>[
                            const SizedBox(height: 14),
                            TextFormField(
                              controller: _passwordConfirm,
                              enabled: !_isSubmitting,
                              obscureText: _obscurePassword,
                              textInputAction: TextInputAction.done,
                              onFieldSubmitted: (_) => _submit(),
                              decoration: const InputDecoration(
                                labelText: 'Confirm password',
                              ),
                              validator: (String? value) {
                                if (value != _password.text) {
                                  return 'Konfirmasi password tidak sama.';
                                }
                                return null;
                              },
                            ),
                          ],
                          if (_error != null) ...<Widget>[
                            const SizedBox(height: 16),
                            InfoBanner(
                              icon: Icons.error_outline,
                              tone: InfoTone.error,
                              message: _error!,
                            ),
                          ],
                          const SizedBox(height: 20),
                          FilledButton(
                            onPressed: _isSubmitting ? null : _submit,
                            child: _isSubmitting
                                ? const SizedBox(
                                    width: 22,
                                    height: 22,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.5,
                                      color: Colors.white,
                                    ),
                                  )
                                : Text(
                                    _isRegister
                                        ? 'Create account'
                                        : 'Sign in',
                                  ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: _isSubmitting ? null : _toggleMode,
                      child: Text(
                        _isRegister
                            ? 'Already have an account? Sign in'
                            : 'No account yet? Create one',
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Your analysis history is visible only to your account.',
                      textAlign: TextAlign.center,
                      style: text.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
