import '../../domain/entities/prediction.dart';

class PredictionResponseModel {
  const PredictionResponseModel({
    required this.label,
    required this.confidence,
    required this.stable,
    required this.history,
  });

  final String label;
  final double confidence;
  final bool stable;
  final List<String> history;

  factory PredictionResponseModel.fromJson(Map<String, dynamic> json) {
    final label = json['label'];
    final confidence = json['confidence'];
    final stable = json['stable'];
    final history = json['history'];

    if (label is! String) {
      throw const FormatException('Prediction response label is invalid.');
    }
    if (confidence is! num) {
      throw const FormatException('Prediction response confidence is invalid.');
    }
    if (stable is! bool) {
      throw const FormatException(
          'Prediction response stable flag is invalid.');
    }
    if (history is! List) {
      throw const FormatException('Prediction response history is invalid.');
    }

    final normalizedConfidence =
        confidence.toDouble().clamp(0.0, 1.0).toDouble();

    return PredictionResponseModel(
      label: label,
      confidence: normalizedConfidence,
      stable: stable,
      history: history.map((item) => item.toString()).toList(),
    );
  }

  Prediction toEntity() {
    return Prediction(
      label: label,
      confidence: confidence,
      stable: stable,
      history: history,
    );
  }
}
