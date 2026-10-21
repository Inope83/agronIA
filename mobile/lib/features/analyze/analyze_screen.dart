import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/theme/app_colors.dart';
import '../../shared/widgets/app_card.dart';

class AnalyzeScreen extends StatefulWidget {
  const AnalyzeScreen({super.key});

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen> {
  static const int _maxImageBytes = 10 * 1024 * 1024;

  static const List<String> _crops = <String>[
    'Rice',
    'Maize',
    'Cassava',
    'Sweet potato',
    'Coffee',
    'Other',
  ];

  final TextEditingController _notesController = TextEditingController();

  XFile? _image;
  Uint8List? _imageBytes;
  String? _selectedCrop;
  bool _isPicking = false;

  bool get _canUseCamera {
    return defaultTargetPlatform == TargetPlatform.android ||
        defaultTargetPlatform == TargetPlatform.iOS;
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    if (_isPicking) {
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

    if (_selectedCrop == null) {
      _showMessage('Select the crop to continue.');
      return;
    }

    await showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: const Text('Analysis is not available yet'),
          content: const Text(
            'The image upload and AI analysis are not connected in this build. '
            'No prediction has been generated for this photo.',
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Understood'),
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
      body: ListView(
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
          DropdownButtonFormField<String>(
            initialValue: _selectedCrop,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Crop',
              helperText: 'Select the plant shown in the photo.',
            ),
            items: _crops
                .map(
                  (String crop) => DropdownMenuItem<String>(
                    value: crop,
                    child: Text(crop),
                  ),
                )
                .toList(),
            onChanged: (String? value) {
              setState(() => _selectedCrop = value);
            },
          ),
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
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: _isPicking ? null : _submit,
            icon: const Icon(Icons.search),
            label: const Text('Analyze image'),
          ),
        ],
      ),
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
                    onPressed:
                        _isPicking ? null : () => _pickImage(ImageSource.gallery),
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
                  onPressed: _removeImage,
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
