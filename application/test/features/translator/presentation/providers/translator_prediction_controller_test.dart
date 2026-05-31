import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:sign_language_translator/features/translator/domain/entities/prediction.dart';
import 'package:sign_language_translator/features/translator/domain/repositories/prediction_repository.dart';
import 'package:sign_language_translator/features/translator/domain/usecases/send_frame_for_prediction.dart';
import 'package:sign_language_translator/features/translator/presentation/providers/translator_prediction_controller.dart';
import 'package:sign_language_translator/features/translator/presentation/services/camera_frame_capture_service.dart';

void main() {
  test('prediction controller captures a frame and updates state', () async {
    final repository = _FakePredictionRepository();
    final controller = TranslatorPredictionController(
      sendFrameForPrediction: SendFrameForPrediction(repository),
      interval: const Duration(days: 1),
      captureFrame: () async {
        return CapturedCameraFrame(
          bytes: Uint8List.fromList([1, 2, 3]),
          filename: 'frame.jpg',
        );
      },
    );

    await controller.startDetection();

    expect(repository.requestCount, 1);
    expect(controller.state.backendStatus, BackendConnectionStatus.connected);
    expect(controller.state.prediction?.label, 'hello');
    expect(controller.state.history, ['hello']);
    expect(controller.state.sentence, 'hello');

    controller.stopDetection();
    controller.dispose();
  });
}

class _FakePredictionRepository implements PredictionRepository {
  int requestCount = 0;

  @override
  Future<Prediction> predictFrame({
    required Uint8List bytes,
    required String filename,
  }) async {
    requestCount++;
    return const Prediction(
      label: 'hello',
      confidence: 0.94,
      stable: true,
      history: ['hello'],
    );
  }
}
