import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class SectionHeader extends StatelessWidget {
  const SectionHeader({super.key, required this.title, this.trailing});

  final String title;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Expanded(
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
        ?trailing,
      ],
    );
  }
}

class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: padding,
        child: child,
      ),
    );
  }
}

class InfoBanner extends StatelessWidget {
  const InfoBanner({
    super.key,
    required this.icon,
    required this.message,
    this.tone = InfoTone.neutral,
  });

  final IconData icon;
  final String message;
  final InfoTone tone;

  @override
  Widget build(BuildContext context) {
    final Color background;
    final Color foreground;

    switch (tone) {
      case InfoTone.neutral:
        background = AppColors.lightGreen;
        foreground = AppColors.darkGreen;
      case InfoTone.warning:
        background = const Color(0xFFFFF8E1);
        foreground = const Color(0xFF8D6E00);
      case InfoTone.error:
        background = const Color(0xFFFDECEA);
        foreground = AppColors.error;
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Icon(icon, color: foreground, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: foreground,
                    height: 1.45,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

enum InfoTone { neutral, warning, error }
