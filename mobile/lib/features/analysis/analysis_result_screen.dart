import 'dart:typed_data';

import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';

class PredictionResult {
  const PredictionResult({
    required this.cropName,
    required this.label,
    required this.explanation,
    this.confidence,
    this.nextSteps = const <String>[],
    this.isUncertain = false,
  });

  final String cropName;
  final String label;
  final String explanation;
  final double? confidence;
  final List<String> nextSteps;
  final bool isUncertain;
}

class AnalysisResultScreen extends StatelessWidget {
  const AnalysisResultScreen({
    super.key,
    required this.imageBytes,
    required this.result,
    required this.onDone,
  });

  final Uint8List imageBytes;
  final PredictionResult result;
  final VoidCallback onDone;

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Analysis result')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 4, 20, 28),
        children: <Widget>[
          ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: Image.memory(imageBytes, fit: BoxFit.cover),
            ),
          ),
          const SizedBox(height: 20),
          Text(result.cropName, style: text.bodySmall),
          const SizedBox(height: 4),
          Text(result.label, style: text.headlineSmall),
          if (result.confidence != null) ...<Widget>[
            const SizedBox(height: 6),
            Text(
              'Model confidence: ${_formatConfidence(result.confidence!)}',
              style: text.bodySmall,
            ),
          ],
          const SizedBox(height: 20),
          if (result.isUncertain) ...<Widget>[
            const InfoBanner(
              icon: Icons.help_outline,
              tone: InfoTone.warning,
              message:
                  'The model could not identify a reliable match for this image. '
                  'Please try a clearer photo or consult an agricultural extension worker.',
            ),
            const SizedBox(height: 16),
          ],
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('What this means', style: text.titleSmall),
                const SizedBox(height: 8),
                Text(result.explanation, style: text.bodyMedium),
              ],
            ),
          ),
          if (result.nextSteps.isNotEmpty) ...<Widget>[
            const SizedBox(height: 14),
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text('Suggested next steps', style: text.titleSmall),
                  const SizedBox(height: 10),
                  ...result.nextSteps.map(
                    (String step) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          const Icon(
                            Icons.check_circle_outline,
                            size: 18,
                            color: AppColors.primary,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(step, style: text.bodyMedium),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 16),
          const InfoBanner(
            icon: Icons.info_outline,
            tone: InfoTone.warning,
            message:
                'This is a preliminary AI prediction, not a confirmed diagnosis. '
                'Verify the condition before applying any treatment.',
          ),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: onDone,
            child: const Text('Back to home'),
          ),
        ],
      ),
    );
  }

  String _formatConfidence(double value) {
    final double percentage = value <= 1 ? value * 100 : value;
    return '${percentage.clamp(0, 100).toStringAsFixed(0)}%';
  }
}
