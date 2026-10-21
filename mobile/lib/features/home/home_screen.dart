import 'package:flutter/material.dart';

import '../../core/session/session_controller.dart';
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.session,
    required this.onAnalyzeTap,
    required this.onHistoryTap,
    required this.onLearnTap,
  });

  final SessionController session;
  final VoidCallback onAnalyzeTap;
  final VoidCallback onHistoryTap;
  final VoidCallback onLearnTap;

  Future<void> _confirmLogout(BuildContext context) async {
    final bool? shouldLogout = await showDialog<bool>(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: const Text('Sign out?'),
          content: const Text(
            'Your saved analyses stay on the server, but you will need to sign in again to view them.',
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: const Text('Sign out'),
            ),
          ],
        );
      },
    );

    if (shouldLogout == true) {
      await session.logout();
    }
  }

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;
    final String name = session.user?.label ?? '';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agronia'),
        actions: <Widget>[
          PopupMenuButton<String>(
            tooltip: 'Account',
            icon: const Icon(Icons.account_circle_outlined),
            onSelected: (String value) {
              if (value == 'logout') {
                _confirmLogout(context);
              }
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              PopupMenuItem<String>(
                enabled: false,
                child: Text(name.isEmpty ? 'Signed in' : name),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem<String>(
                value: 'logout',
                child: Text('Sign out'),
              ),
            ],
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 4, 20, 28),
        children: <Widget>[
          Text(
            name.isEmpty ? 'Welcome' : 'Welcome, $name',
            style: text.displaySmall,
          ),
          const SizedBox(height: 6),
          Text(
            'Check your crops for signs of disease and get clear, honest next steps.',
            style: text.bodyMedium?.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: 24),
          _AnalyzeCard(onTap: onAnalyzeTap),
          const SizedBox(height: 14),
          _LinkCard(
            icon: Icons.history,
            title: 'Analysis history',
            subtitle: 'Review the crops you have analyzed.',
            onTap: onHistoryTap,
          ),
          const SizedBox(height: 10),
          _LinkCard(
            icon: Icons.menu_book_outlined,
            title: 'Learn about crop care',
            subtitle: 'Practical guidance on keeping crops healthy.',
            onTap: onLearnTap,
          ),
          const SizedBox(height: 24),
          const InfoBanner(
            icon: Icons.info_outline,
            message:
                'Agronia provides preliminary AI predictions, not confirmed diagnoses. '
                'Always verify findings with an agricultural extension worker before acting.',
          ),
        ],
      ),
    );
  }
}

class _AnalyzeCard extends StatelessWidget {
  const _AnalyzeCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;

    return Material(
      color: AppColors.primary,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: <Widget>[
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(
                  Icons.camera_alt_outlined,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      'Analyze crop image',
                      style: text.titleMedium?.copyWith(color: Colors.white),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Choose a clear photo of the affected plant part.',
                      style: text.bodySmall?.copyWith(
                        color: Colors.white.withValues(alpha: 0.85),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.arrow_forward, color: Colors.white),
            ],
          ),
        ),
      ),
    );
  }
}

class _LinkCard extends StatelessWidget {
  const _LinkCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: EdgeInsets.zero,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: <Widget>[
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: AppColors.lightGreen,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: AppColors.primary),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textSecondary),
            ],
          ),
        ),
      ),
    );
  }
}
