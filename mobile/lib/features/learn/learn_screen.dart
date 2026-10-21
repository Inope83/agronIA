import 'package:flutter/material.dart';

import '../../shared/widgets/empty_state.dart';

class LearnScreen extends StatelessWidget {
  const LearnScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Learn')),
      body: const EmptyState(
        icon: Icons.menu_book_outlined,
        title: 'Learning content is not available yet',
        message:
            'Reviewed guidance on crop health and disease prevention will be published here in a later release.',
      ),
    );
  }
}
