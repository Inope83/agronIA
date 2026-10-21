import 'package:flutter/material.dart';

import '../../shared/widgets/empty_state.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('History')),
      body: const EmptyState(
        icon: Icons.history,
        title: 'No analyses yet',
        message:
            'Your submitted crop photos and results will appear here once analysis is available.',
      ),
    );
  }
}
