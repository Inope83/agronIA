class AuthUser {
  const AuthUser({
    required this.id,
    required this.username,
    this.email,
    this.displayName,
  });

  final int id;
  final String username;
  final String? email;
  final String? displayName;

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    final Object? profile = json['profile'];
    String? displayName;
    if (profile is Map<String, dynamic>) {
      final Object? value = profile['display_name'];
      if (value is String && value.isNotEmpty) {
        displayName = value;
      }
    }

    return AuthUser(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? '',
      email: json['email'] as String?,
      displayName: displayName,
    );
  }

  String get label {
    if (displayName != null) {
      return displayName!;
    }
    return username;
  }
}

class AuthSession {
  const AuthSession({required this.token, required this.user});

  final String token;
  final AuthUser user;
}

class CropOption {
  const CropOption({required this.code, required this.name});

  final String code;
  final String name;

  factory CropOption.fromJson(Map<String, dynamic> json) {
    return CropOption(
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
    );
  }
}

class Prediction {
  const Prediction({
    this.classId,
    this.label,
    this.confidence,
    this.modelVersion,
    this.isConfident = false,
  });

  final String? classId;
  final String? label;
  final double? confidence;
  final String? modelVersion;
  final bool isConfident;

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      classId: json['class_id'] as String?,
      label: json['label'] as String?,
      confidence: _asDouble(json['confidence']),
      modelVersion: json['model_version'] as String?,
      isConfident: json['is_confident'] as bool? ?? false,
    );
  }
}

class DiseaseInfo {
  const DiseaseInfo({
    required this.code,
    required this.name,
    this.nameLocal,
    this.symptoms = '',
    this.prevention = '',
    this.management = '',
    this.source = '',
  });

  final String code;
  final String name;
  final String? nameLocal;
  final String symptoms;
  final String prevention;
  final String management;
  final String source;

  bool get isHealthy => code == 'padi-sehat';

  factory DiseaseInfo.fromJson(Map<String, dynamic> json) {
    return DiseaseInfo(
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameLocal: json['name_local'] as String?,
      symptoms: json['symptoms'] as String? ?? '',
      prevention: json['prevention'] as String? ?? '',
      management: json['management'] as String? ?? '',
      source: json['source'] as String? ?? '',
    );
  }
}

class AnalysisFeedback {
  const AnalysisFeedback({
    required this.isCorrect,
    this.suggestedDisease,
    this.note = '',
  });

  final bool isCorrect;
  final String? suggestedDisease;
  final String note;

  factory AnalysisFeedback.fromJson(Map<String, dynamic> json) {
    return AnalysisFeedback(
      isCorrect: json['is_correct'] as bool? ?? false,
      suggestedDisease: json['suggested_disease'] as String?,
      note: json['note'] as String? ?? '',
    );
  }
}

class AnalysisRecord {
  const AnalysisRecord({
    required this.id,
    required this.status,
    required this.message,
    this.crop,
    this.predictedDisease,
    this.confidence,
    this.modelVersion,
    this.imageUrl,
    this.prediction,
    this.disease,
    this.feedback,
    this.createdAt,
  });

  final String id;
  final String status;
  final String message;
  final String? crop;
  final String? predictedDisease;
  final double? confidence;
  final String? modelVersion;
  final String? imageUrl;
  final Prediction? prediction;
  final DiseaseInfo? disease;
  final AnalysisFeedback? feedback;
  final DateTime? createdAt;

  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isProcessing => status == 'processing' || status == 'pending';
  bool get hasPrediction => isCompleted && prediction != null;

  String get label {
    if (prediction?.label != null && prediction!.label!.isNotEmpty) {
      return prediction!.label!;
    }
    if (predictedDisease != null && predictedDisease!.isNotEmpty) {
      return predictedDisease!;
    }
    return isFailed ? 'Analysis failed' : 'Analysis in progress';
  }

  factory AnalysisRecord.fromJson(Map<String, dynamic> json) {
    final Object? predictionJson = json['prediction'];
    final Prediction? prediction = predictionJson is Map<String, dynamic>
        ? Prediction.fromJson(predictionJson)
        : null;
    final Object? diseaseJson = json['disease'];
    final DiseaseInfo? disease = diseaseJson is Map<String, dynamic>
        ? DiseaseInfo.fromJson(diseaseJson)
        : null;
    final Object? feedbackJson = json['feedback'];
    final AnalysisFeedback? feedback = feedbackJson is Map<String, dynamic>
        ? AnalysisFeedback.fromJson(feedbackJson)
        : null;

    return AnalysisRecord(
      id: json['id'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      message: json['message'] as String? ?? '',
      crop: json['crop'] as String?,
      predictedDisease: json['predicted_disease'] as String?,
      confidence: _asDouble(json['confidence']) ?? prediction?.confidence,
      modelVersion: json['model_version'] as String?,
      imageUrl: json['image_url'] as String?,
      prediction: prediction,
      disease: disease,
      feedback: feedback,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    );
  }
}

double? _asDouble(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return null;
}
