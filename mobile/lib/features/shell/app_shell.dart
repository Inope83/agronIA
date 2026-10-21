import 'package:flutter/material.dart';

import '../../core/session/session_controller.dart';
import '../analyze/analyze_screen.dart';
import '../history/history_screen.dart';
import '../home/home_screen.dart';
import '../learn/learn_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key, required this.session});

  final SessionController session;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;
  final GlobalKey<HistoryScreenState> _historyKey = GlobalKey<HistoryScreenState>();

  late final List<Widget> _screens = <Widget>[
    HomeScreen(
      session: widget.session,
      onAnalyzeTap: () => _selectTab(1),
      onHistoryTap: () => _selectTab(2),
      onLearnTap: () => _selectTab(3),
    ),
    AnalyzeScreen(
      session: widget.session,
      onGoHome: () => _selectTab(0),
    ),
    HistoryScreen(key: _historyKey, session: widget.session),
    const LearnScreen(),
  ];

  void _selectTab(int index) {
    setState(() => _selectedIndex = index);
    if (index == 2) {
      _historyKey.currentState?.reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: IndexedStack(index: _selectedIndex, children: _screens),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _selectTab,
        destinations: const <NavigationDestination>[
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt),
            label: 'Analyze',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book),
            label: 'Learn',
          ),
        ],
      ),
    );
  }
}
