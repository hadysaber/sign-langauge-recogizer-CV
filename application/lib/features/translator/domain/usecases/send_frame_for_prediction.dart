import 'dart:typed_data';

import '../entities/prediction.dart';
import '../repositories/prediction_repository.dart';

class SendFrameForPrediction {
  const SendFrameForPrediction(this._repository);

  final PredictionRepository _repository;

  Future<Prediction> call({
    required Uint8List bytes,
    required String filename,
  }) {
    return _repository.predictFrame(bytes: bytes, filename: filename);
  }
}
