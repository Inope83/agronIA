import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/api/api_exception.dart';
import '../../core/api/models.dart';
import '../../core/session/session_controller.dart';
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';
import '../analysis/analysis_result_screen.dart';

class AnalyzeScreen extends StatefulWidget {
  const AnalyzeScreen({
    super.key,
    required this.session,
    required this.onGoHome,
  });

  final SessionController session;
  final VoidCallback onGoHome;

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen> {
  static const int _maxImageBytes = 10 * 1024 * 1024;

  final TextEditingController _notesController = TextEditingController();

  XFile? _image;
  Uint8List? _imageBytes;
  String? _selectedCrop;
  List<CropOption> _crops = <CropOption>[];
  bool _isLoadingCrops = true;
  String? _cropError;
  bool _isPicking = false;
  bool _isSubmitting = false;

  bool get _canUseCamera {
    return defaultTargetPlatform == TargetPlatform.android ||
        defaultTargetPlatform == TargetPlatform.iOS;
  }

  @override
  void initState() {
    super.initState();
    _loadCrops();
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadCrops() async {
    setState(() {
      _isLoadingCrops = true;
      _cropError = null;
    });

    try {
      final List<CropOption> crops = await widget.session.api.fetchCrops();
      if (!mounted) {
        return;
      }
      setState(() => _crops = crops);
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() => _cropError = error.message);
    } finally {
      if (mounted) {
        setState(() => _isLoadingCrops = false);
      }
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    if (_isPicking || _isSubmitting) {
      return;
    }

    setState(() => _isPicking = true);

    try {
      final ImagePicker picker = ImagePicker();
      final XFile? file = await picker.pickImage(
        source: source,
        maxWidth: 1600,
        imageQuality: 85,
      );

      if (file == null) {
        return;
      }

      final String name = file.name.toLowerCase();
      final bool hasSupportedExtension = name.endsWith('.jpg') ||
          name.endsWith('.jpeg') ||
          name.endsWith('.png');

      if (!hasSupportedExtension) {
        _showMessage('Only JPG and PNG images are supported.');
        return;
      }

      final Uint8List bytes = await file.readAsBytes();

      if (bytes.lengthInBytes > _maxImageBytes) {
        _showMessage('The image is larger than 10 MB. Choose a smaller photo.');
        return;
      }

      if (!mounted) {
        return;
      }

      setState(() {
        _image = file;
        _imageBytes = bytes;
      });
    } catch (_) {
      _showMessage('The image picker could not be opened on this device.');
    } finally {
      if (mounted) {
        setState(() => _isPicking = false);
      }
    }
  }

  void _removeImage() {
    setState(() {
      _image = null;
      _imageBytes = null;
    });
  }

  void _showMessage(String message) {
    if (!mounted) {
      return;
    }

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _submit() async {
    if (_imageBytes == null) {
      _showMessage('Select a photo of the affected crop first.');
      return;
    }

    FocusScope.of(context).unfocus();
    setState(() => _isSubmitting = true);

    try {
      final AnalysisRecord record = await widget.session.api.createAnalysis(
        bytes: _imageBytes!,
        filename: _image?.name ?? 'crop.jpg',
        crop: _selectedCrop,
      );

      if (!mounted) {
        return;
      }

      if (record.hasPrediction) {
        await Navigator.of(context).push(
          MaterialPageRoute<void>(
            builder: (BuildContext routeContext) => AnalysisResultScreen(
              imageBytes: _imageBytes!,
              result: PredictionResult.fromRecord(record),
              api: widget.session.api,
              onDone: () {
                Navigator.of(routeContext).pop();
                widget.onGoHome();
              },
            ),
          ),
        );
      } else {
        await _showFailure(
          record.message.isNotEmpty
              ? record.message
              : 'The analysis did not produce a result.',
        );
      }
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      if (error.isUnauthorized) {
        await widget.session.logout();
        if (mounted) {
          _showMessage('Sesi berakhir. Silakan masuk lagi.');
        }
      } else {
        await _showFailure(error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  Future<void> _showFailure(String message) {
    return showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: const Text('Analysis not completed'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(message),
              const SizedBox(height: 12),
              Text(
                'No diagnosis was produced for this photo.',
                style: Theme.of(dialogContext).textTheme.bodySmall,
              ),
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
    final TextTheme text = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Analyze')),
      body: AbsorbPointer(
        absorbing: _isSubmitting,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 4, 20, 28),
          children: <Widget>[
            Text('Analyze a crop image', style: text.headlineSmall),
            const SizedBox(height: 6),
            Text(
              'Photograph the affected leaf, stem, or fruit in good lighting. '
              'Include both healthy and affected areas when possible.',
              style: text.bodyMedium?.copyWith(color: AppColors.textSecondary),
            ),
            const SizedBox(height: 20),
            _buildImageSection(context),
            const SizedBox(height: 20),
            _buildCropField(context),
            const SizedBox(height: 16),
            TextField(
              controller: _notesController,
              minLines: 3,
              maxLines: 5,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                labelText: 'Visible symptoms (optional)',
                hintText: 'For example: yellow spots on the lower leaves',
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 20),
            const InfoBanner(
              icon: Icons.tips_and_updates_outlined,
              message:
                  'Clear photos taken in daylight, with the affected area in focus, '
                  'usually provide more useful visual information.',
            ),
            if (_isSubmitting) ...<Widget>[
              const SizedBox(height: 18),
              const _SubmittingNotice(),
            ],
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: _isSubmitting ? null : _submit,
              icon: _isSubmitting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.search),
              label: Text(
                _isSubmitting ? 'Analyzing image...' : 'Analyze image',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCropField(BuildContext context) {
    if (_isLoadingCrops) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 8),
        child: LinearProgressIndicator(minHeight: 3),
      );
    }

    if (_cropError != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          InfoBanner(
            icon: Icons.warning_amber_outlined,
            tone: InfoTone.warning,
            message: 'Daftar tanaman tidak dapat dimuat. ${_cropError!}',
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: _loadCrops,
              child: const Text('Try again'),
            ),
          ),
        ],
      );
    }

    if (_crops.isEmpty) {
      return const InfoBanner(
        icon: Icons.info_outline,
        message:
            'Belum ada data tanaman di server. Analisis tetap dapat dijalankan tanpa memilih tanaman.',
      );
    }

    return DropdownButtonFormField<String>(
      initialValue: _selectedCrop,
      isExpanded: true,
      decoration: const InputDecoration(
        labelText: 'Crop (optional)',
        helperText: 'Select the plant shown in the photo.',
      ),
      items: _crops
          .map(
            (CropOption crop) => DropdownMenuItem<String>(
              value: crop.code,
              child: Text(crop.name),
            ),
          )
          .toList(),
      onChanged: (String? value) {
        setState(() => _selectedCrop = value);
      },
    );
  }

  Widget _buildImageSection(BuildContext context) {
    if (_imageBytes == null) {
      return AppCard(
        child: Column(
          children: <Widget>[
            Container(
              width: double.infinity,
              height: 180,
              decoration: BoxDecoration(
                color: AppColors.lightGreen,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border),
              ),
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Icon(
                    Icons.add_photo_alternate_outlined,
                    size: 42,
                    color: AppColors.primary,
                  ),
                  SizedBox(height: 10),
                  Text(
                    'No image selected',
                    style: TextStyle(
                      color: AppColors.darkGreen,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: <Widget>[
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isPicking
                        ? null
                        : () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined),
                    label: const Text('Gallery'),
                  ),
                ),
                if (_canUseCamera) ...<Widget>[
                  const SizedBox(width: 12),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: _isPicking
                          ? null
                          : () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.photo_camera_outlined),
                      label: const Text('Camera'),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      );
    }

    return AppCard(
      padding: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          ClipRRect(
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(14),
            ),
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: Image.memory(
                _imageBytes!,
                fit: BoxFit.cover,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Text(
                    _image?.name ?? 'Selected image',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: _isSubmitting ? null : _removeImage,
                  icon: const Icon(Icons.close, size: 18),
                  label: const Text('Remove'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SubmittingNotice extends StatelessWidget {
  const _SubmittingNotice();

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Row(
        children: <Widget>[
          const SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(strokeWidth: 2.5),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              'Uploading the image and waiting for the analysis result. '
              'Keep the app open.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}
