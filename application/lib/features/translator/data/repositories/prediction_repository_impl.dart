import 'dart:typed_data';

import '../../domain/entities/prediction.dart';
import '../../domain/repositories/prediction_repository.dart';
import '../services/translator_api_client.dart';

class PredictionRepositoryImpl implements PredictionRepository {
  const PredictionRepositoryImpl(this._apiClient);

  final TranslatorApiClient _apiClient;

  @override
  Future<Prediction> predictFrame({
    required Uint8List bytes,
    required String filename,
  }) async {
    final model = await _apiClient.predictFrame(
      bytes: bytes,
      filename: filename,
    );
    return model.toEntity();
  }
}
