import 'package:flutter/material.dart';

import 'core/api/api_client.dart';
import 'core/session/session_controller.dart';
import 'core/session/token_store.dart';
import 'core/theme/app_colors.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/auth_screen.dart';
import 'features/shell/app_shell.dart';
import 'shared/widgets/status_states.dart';

class AgroniaApp extends StatefulWidget {
  const AgroniaApp({super.key, this.session});

  final SessionController? session;

  @override
  State<AgroniaApp> createState() => _AgroniaAppState();
}

class _AgroniaAppState extends State<AgroniaApp> {
  late final SessionController _session = widget.session ??
      SessionController(
        api: ApiClient(),
        tokenStore: SecureTokenStore(),
      );

  @override
  void initState() {
    super.initState();
    _session.initialize();
  }

  @override
  void dispose() {
    if (widget.session == null) {
      _session.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Agronia',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: ListenableBuilder(
        listenable: _session,
        builder: (BuildContext context, Widget? child) {
          if (_session.isInitializing) {
            return const _SplashScreen();
          }

          if (_session.initializationError != null) {
            return Scaffold(
              body: ErrorState(
                title: 'Cannot reach the server',
                message: _session.initializationError!,
                onRetry: _session.initialize,
              ),
            );
          }

          if (!_session.isAuthenticated) {
            return AuthScreen(session: _session);
          }

          return AppShell(session: _session);
        },
      ),
    );
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Container(
              width: 84,
              height: 84,
              decoration: const BoxDecoration(
                color: AppColors.lightGreen,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.eco,
                size: 42,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 18),
            Text(
              'Agronia',
              style: Theme.of(context).textTheme.displaySmall,
            ),
            const SizedBox(height: 24),
            const SizedBox(
              width: 26,
              height: 26,
              child: CircularProgressIndicator(strokeWidth: 2.5),
            ),
          ],
        ),
      ),
    );
  }
}
