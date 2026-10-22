import 'dart:typed_data';

import 'package:flutter/material.dart';

import '../../core/api/api_exception.dart';
import '../../core/api/models.dart';
import '../../core/session/session_controller.dart';
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/empty_state.dart';
import '../../shared/widgets/status_states.dart';
import '../analysis/analysis_result_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, required this.session});

  final SessionController session;

  @override
  State<HistoryScreen> createState() => HistoryScreenState();
}

class HistoryScreenState extends State<HistoryScreen> {
  List<AnalysisRecord> _records = <AnalysisRecord>[];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    reload();
  }

  Future<void> reload() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final List<AnalysisRecord> records =
          await widget.session.api.fetchAnalyses();
      if (!mounted) {
        return;
      }
      setState(() => _records = records);
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      if (error.isUnauthorized) {
        await widget.session.logout();
        return;
      }
      setState(() => _error = error.message);
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _openRecord(AnalysisRecord record) async {
    if (record.isProcessing) {
      await _showInfo(
        title: 'Analysis in progress',
        message:
            'This analysis has not finished yet. Check the history again shortly.',
      );
      return;
    }

    if (!record.hasPrediction) {
      await _showInfo(
        title: 'Analysis not completed',
        message: record.message.isNotEmpty
            ? record.message
            : 'The server did not return a prediction for this record.',
        isFailure: record.isFailed,
      );
      return;
    }

    Uint8List? imageBytes;
    if (record.imageUrl != null) {
      try {
        imageBytes = await widget.session.api.fetchImage(record.imageUrl!);
      } on ApiException {
        imageBytes = null;
      }
    }

    if (!mounted) {
      return;
    }

    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (BuildContext routeContext) => AnalysisResultScreen(
          imageBytes: imageBytes,
          result: PredictionResult.fromRecord(record),
          api: widget.session.api,
          onDone: () => Navigator.of(routeContext).pop(),
        ),
      ),
    );
  }

  Future<void> _showInfo({
    required String title,
    required String message,
    bool isFailure = false,
  }) {
    return showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: Text(title),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(message),
              if (isFailure) ...<Widget>[
                const SizedBox(height: 12),
                Text(
                  'No diagnosis was produced for this photo.',
                  style: Theme.of(dialogContext).textTheme.bodySmall,
                ),
              ],
            ],
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('History'),
        actions: <Widget>[
          IconButton(
            tooltip: 'Refresh',
            onPressed: _isLoading ? null : reload,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const LoadingState(
        title: 'Loading your analyses',
        message: 'Fetching your analysis history from the server.',
      );
    }

    if (_error != null) {
      return ErrorState(
        title: 'History could not be loaded',
        message: _error!,
        onRetry: reload,
      );
    }

    if (_records.isEmpty) {
      return const EmptyState(
        icon: Icons.history,
        title: 'No analyses yet',
        message:
            'Your submitted crop photos and results will appear here after you analyze an image.',
      );
    }

    return RefreshIndicator(
      onRefresh: reload,
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
        itemCount: _records.length,
        separatorBuilder: (_, _) => const SizedBox(height: 10),
        itemBuilder: (BuildContext context, int index) {
          return _HistoryTile(
            record: _records[index],
            onTap: () => _openRecord(_records[index]),
          );
        },
      ),
    );
  }
}

class _HistoryTile extends StatelessWidget {
  const _HistoryTile({required this.record, required this.onTap});

  final AnalysisRecord record;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;
    final Color accent;
    final IconData icon;

    if (record.isCompleted) {
      accent = AppColors.primary;
      icon = Icons.check_circle_outline;
    } else if (record.isFailed) {
      accent = AppColors.error;
      icon = Icons.error_outline;
    } else {
      accent = AppColors.warning;
      icon = Icons.hourglass_empty;
    }

    final String subtitle = record.message.isNotEmpty
        ? record.message
        : _formatDate(record.createdAt);

    return Material(
      color: AppColors.white,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.border),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: accent, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      record.label,
                      style: text.titleSmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: text.bodySmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatDate(record.createdAt),
                      style: text.bodySmall?.copyWith(fontSize: 12),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 6),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime? value) {
    if (value == null) {
      return '';
    }
    const List<String> months = <String>[
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    final DateTime local = value.toLocal();
    final String hour = local.hour.toString().padLeft(2, '0');
    final String minute = local.minute.toString().padLeft(2, '0');
    return '${local.day} ${months[local.month - 1]} ${local.year}, $hour:$minute';
  }
}
