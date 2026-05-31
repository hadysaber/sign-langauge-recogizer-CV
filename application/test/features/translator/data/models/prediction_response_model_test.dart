import 'package:flutter_test/flutter_test.dart';
import 'package:sign_language_translator/features/translator/data/models/prediction_response_model.dart';

void main() {
  group('PredictionResponseModel', () {
    test('parses valid backend response', () {
      final model = PredictionResponseModel.fromJson({
        'label': 'hello',
        'confidence': 0.94,
        'stable': true,
        'history': ['hello'],
      });

      expect(model.label, 'hello');
      expect(model.confidence, 0.94);
      expect(model.stable, isTrue);
      expect(model.history, ['hello']);
    });

    test('throws FormatException for invalid response', () {
      expect(
        () => PredictionResponseModel.fromJson({
          'label': 'hello',
          'confidence': 'high',
          'stable': true,
          'history': ['hello'],
        }),
        throwsFormatException,
      );
    });
  });
}
