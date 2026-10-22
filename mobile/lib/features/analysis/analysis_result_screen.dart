import 'dart:typed_data';

import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../../core/api/api_exception.dart';
import '../../core/api/models.dart';
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';

class PredictionResult {
  const PredictionResult({
    required this.analysisId,
    required this.cropName,
    required this.label,
    required this.explanation,
    this.confidence,
    this.nextSteps = const <String>[],
    this.isUncertain = false,
    this.disease,
    this.feedback,
    this.modelVersion,
  });

  factory PredictionResult.fromRecord(AnalysisRecord record) {
    final Prediction? prediction = record.prediction;
    return PredictionResult(
      analysisId: record.id,
      cropName: record.crop ?? 'Crop not specified',
      label: prediction?.label ?? record.predictedDisease ?? 'Unknown condition',
      explanation: record.message,
      confidence: record.confidence ?? prediction?.confidence,
      isUncertain: !(prediction?.isConfident ?? false),
      disease: record.disease,
      feedback: record.feedback,
      modelVersion: record.modelVersion ?? prediction?.modelVersion,
    );
  }

  final String analysisId;
  final String cropName;
  final String label;
  final String explanation;
  final double? confidence;
  final List<String> nextSteps;
  final bool isUncertain;
  final DiseaseInfo? disease;
  final AnalysisFeedback? feedback;
  final String? modelVersion;
}

class AnalysisResultScreen extends StatefulWidget {
  const AnalysisResultScreen({
    super.key,
    required this.imageBytes,
    required this.result,
    required this.onDone,
    this.api,
  });

  final Uint8List? imageBytes;
  final PredictionResult result;
  final VoidCallback onDone;
  final ApiClient? api;

  @override
  State<AnalysisResultScreen> createState() => _AnalysisResultScreenState();
}

class _AnalysisResultScreenState extends State<AnalysisResultScreen> {
  AnalysisFeedback? _feedback;

  @override
  void initState() {
    super.initState();
    _feedback = widget.result.feedback;
  }

  Future<void> _openFeedbackSheet() async {
    final ApiClient? api = widget.api;
    if (api == null) {
      return;
    }

    final AnalysisFeedback? feedback =
        await showModalBottomSheet<AnalysisFeedback>(
      context: context,
      isScrollControlled: true,
      builder: (BuildContext sheetContext) => _FeedbackSheet(
        api: api,
        analysisId: widget.result.analysisId,
        initial: _feedback,
      ),
    );

    if (!mounted || feedback == null) {
      return;
    }

    setState(() => _feedback = feedback);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(content: Text('Thank you. Your report was saved.')),
      );
  }

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;
    final DiseaseInfo? disease = widget.result.disease;
    final bool isHealthy = disease?.isHealthy ?? false;

    return Scaffold(
      appBar: AppBar(title: const Text('Analysis result')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 4, 20, 28),
        children: <Widget>[
          if (widget.imageBytes != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: AspectRatio(
                aspectRatio: 4 / 3,
                child: Image.memory(widget.imageBytes!, fit: BoxFit.cover),
              ),
            )
          else
            Container(
              height: 140,
              decoration: BoxDecoration(
                color: AppColors.lightGreen,
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Center(
                child: Icon(
                  Icons.image_not_supported_outlined,
                  size: 34,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          const SizedBox(height: 20),
          Text(widget.result.cropName, style: text.bodySmall),
          const SizedBox(height: 4),
          Text(widget.result.label, style: text.headlineSmall),
          if (widget.result.confidence != null) ...<Widget>[
            const SizedBox(height: 6),
            Text(
              'Model confidence: ${_formatConfidence(widget.result.confidence!)}',
              style: text.bodySmall,
            ),
          ],
          if (widget.result.modelVersion != null &&
              widget.result.modelVersion!.isNotEmpty) ...<Widget>[
            const SizedBox(height: 2),
            Text('Model: ${widget.result.modelVersion}', style: text.bodySmall),
          ],
          const SizedBox(height: 16),
          const InfoBanner(
            icon: Icons.info_outline,
            tone: InfoTone.warning,
            message:
                'This is a preliminary AI prediction, not a confirmed diagnosis. '
                'High confidence does not guarantee correctness. Check the symptoms '
                'yourself and consult an agricultural extension worker before treatment.',
          ),
          if (widget.result.isUncertain) ...<Widget>[
            const SizedBox(height: 12),
            const InfoBanner(
              icon: Icons.help_outline,
              tone: InfoTone.warning,
              message:
                  'The model was not confident about this photo. Try a clearer '
                  'close-up of the affected leaf or consult an extension worker.',
            ),
          ],
          if (isHealthy) ...<Widget>[
            const SizedBox(height: 12),
            const InfoBanner(
              icon: Icons.eco_outlined,
              message:
                  'The model did not detect one of the four supported rice '
                  'diseases. This does not rule out early or unsupported problems; '
                  'keep monitoring the crop.',
            ),
          ],
          const SizedBox(height: 16),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('About this prediction', style: text.titleSmall),
                const SizedBox(height: 8),
                Text(
                  disease == null
                      ? (widget.result.explanation.isNotEmpty
                          ? widget.result.explanation
                          : 'The server returned a prediction without additional '
                              'disease information.')
                      : isHealthy
                          ? 'The model classified this photo as a healthy rice '
                              'leaf. This is a preliminary result based only on '
                              'the image.'
                          : 'The model matched this photo to '
                              '${widget.result.label}. This is a preliminary '
                              'result based only on the image, not a laboratory '
                              'test.',
                  style: text.bodyMedium,
                ),
              ],
            ),
          ),
          if (disease != null) ...<Widget>[
            if (disease.symptoms.trim().isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              _TextCard(
                title: isHealthy
                    ? 'What a healthy leaf looks like'
                    : 'Symptoms to check',
                body: disease.symptoms,
              ),
            ],
            if (disease.prevention.trim().isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              _TextCard(title: 'Prevention', body: disease.prevention),
            ],
            if (disease.management.trim().isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              _TextCard(title: 'What to do next', body: disease.management),
            ],
            if (disease.source.trim().isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              Text(
                'Source: ${disease.source}',
                style: text.bodySmall,
              ),
            ],
          ],
          if (widget.result.nextSteps.isNotEmpty) ...<Widget>[
            const SizedBox(height: 12),
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text('Suggested next steps', style: text.titleSmall),
                  const SizedBox(height: 10),
                  ...widget.result.nextSteps.map(
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
          if (widget.api != null) ...<Widget>[
            const SizedBox(height: 16),
            if (_feedback == null)
              OutlinedButton.icon(
                onPressed: _openFeedbackSheet,
                icon: const Icon(Icons.flag_outlined),
                label: const Text('Report incorrect result'),
              )
            else
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text('Your report', style: text.titleSmall),
                    const SizedBox(height: 8),
                    Text(
                      _feedback!.isCorrect
                          ? 'You marked this prediction as correct.'
                          : 'You marked this prediction as incorrect. Thank you '
                              'for helping us improve the model.',
                      style: text.bodyMedium,
                    ),
                    if (_feedback!.note.trim().isNotEmpty) ...<Widget>[
                      const SizedBox(height: 6),
                      Text(
                        'Note: ${_feedback!.note}',
                        style: text.bodySmall,
                      ),
                    ],
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: _openFeedbackSheet,
                      child: const Text('Update report'),
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
                'Do not apply treatment based only on this result. Confirm the '
                'condition first, especially before using any chemical product.',
          ),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: widget.onDone,
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

class _TextCard extends StatelessWidget {
  const _TextCard({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(title, style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          Text(body, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}

class _FeedbackSheet extends StatefulWidget {
  const _FeedbackSheet({
    required this.api,
    required this.analysisId,
    this.initial,
  });

  final ApiClient api;
  final String analysisId;
  final AnalysisFeedback? initial;

  @override
  State<_FeedbackSheet> createState() => _FeedbackSheetState();
}

class _FeedbackSheetState extends State<_FeedbackSheet> {
  static const String _notSure = '__not_sure__';

  final TextEditingController _noteController = TextEditingController();

  bool? _isCorrect;
  String? _suggestedDisease;
  List<DiseaseInfo> _diseases = <DiseaseInfo>[];
  bool _isLoadingDiseases = true;
  bool _isSubmitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _isCorrect = widget.initial?.isCorrect;
    _suggestedDisease = widget.initial?.suggestedDisease;
    _noteController.text = widget.initial?.note ?? '';
    _loadDiseases();
  }

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _loadDiseases() async {
    try {
      final List<DiseaseInfo> diseases = await widget.api.fetchDiseases();
      if (!mounted) {
        return;
      }
      setState(() => _diseases = diseases);
    } on ApiException {
      // Tanpa daftar penyakit, pengguna tetap bisa mengirim catatan.
    } finally {
      if (mounted) {
        setState(() => _isLoadingDiseases = false);
      }
    }
  }

  Future<void> _submit() async {
    if (_isCorrect == null || _isSubmitting) {
      return;
    }

    setState(() {
      _isSubmitting = true;
      _error = null;
    });

    try {
      final AnalysisFeedback feedback = await widget.api.submitFeedback(
        analysisId: widget.analysisId,
        isCorrect: _isCorrect!,
        suggestedDisease: _isCorrect == false &&
                _suggestedDisease != null &&
                _suggestedDisease != _notSure
            ? _suggestedDisease
            : null,
        note: _noteController.text,
      );

      if (!mounted) {
        return;
      }
      Navigator.of(context).pop(feedback);
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() => _error = error.message);
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;
    final List<DiseaseInfo> options = _diseases;

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          20,
          20,
          20,
          20 + MediaQuery.of(context).viewInsets.bottom,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Expanded(
                    child: Text('Report this result', style: text.titleLarge),
                  ),
                  IconButton(
                    onPressed: _isSubmitting
                        ? null
                        : () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                'Was the model prediction correct?',
                style: text.bodyMedium,
              ),
              const SizedBox(height: 14),
              SegmentedButton<bool>(
                segments: const <ButtonSegment<bool>>[
                  ButtonSegment<bool>(
                    value: true,
                    label: Text('Correct'),
                    icon: Icon(Icons.check, size: 18),
                  ),
                  ButtonSegment<bool>(
                    value: false,
                    label: Text('Incorrect'),
                    icon: Icon(Icons.close, size: 18),
                  ),
                ],
                selected: _isCorrect == null
                    ? const <bool>{}
                    : <bool>{_isCorrect!},
                emptySelectionAllowed: true,
                onSelectionChanged: _isSubmitting
                    ? null
                    : (Set<bool> selection) {
                        setState(() {
                          _isCorrect =
                              selection.isEmpty ? null : selection.first;
                          if (_isCorrect == true) {
                            _suggestedDisease = null;
                          }
                        });
                      },
              ),
              if (_isCorrect == false) ...<Widget>[
                const SizedBox(height: 16),
                if (_isLoadingDiseases)
                  const LinearProgressIndicator()
                else if (options.isNotEmpty)
                  DropdownButtonFormField<String>(
                    key: ValueKey<String?>(_suggestedDisease),
                    initialValue: _suggestedDisease,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'What do you think it is? (optional)',
                    ),
                    items: <DropdownMenuItem<String>>[
                      const DropdownMenuItem<String>(
                        value: _notSure,
                        child: Text('Not sure'),
                      ),
                      ...options.map(
                        (DiseaseInfo disease) => DropdownMenuItem<String>(
                          value: disease.code,
                          child: Text(disease.name),
                        ),
                      ),
                    ],
                    onChanged: _isSubmitting
                        ? null
                        : (String? value) {
                            setState(() => _suggestedDisease = value);
                          },
                  ),
                const SizedBox(height: 12),
                TextField(
                  controller: _noteController,
                  maxLines: 3,
                  maxLength: 1000,
                  enabled: !_isSubmitting,
                  decoration: const InputDecoration(
                    labelText: 'What did you see? (optional)',
                    hintText: 'Example: the lesion is long and follows the leaf vein.',
                  ),
                ),
              ],
              if (_error != null) ...<Widget>[
                const SizedBox(height: 8),
                Text(
                  _error!,
                  style: text.bodySmall?.copyWith(color: AppColors.error),
                ),
              ],
              const SizedBox(height: 16),
              FilledButton(
                onPressed:
                    _isCorrect == null || _isSubmitting ? null : _submit,
                child: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Submit report'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
