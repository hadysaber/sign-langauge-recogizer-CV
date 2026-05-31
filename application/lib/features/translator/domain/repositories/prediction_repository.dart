import 'dart:typed_data';

import '../entities/prediction.dart';

abstract class PredictionRepository {
  Future<Prediction> predictFrame({
    required Uint8List bytes,
    required String filename,
  });
}
