import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../../../core/config/backend_config.dart';
import '../models/prediction_response_model.dart';

class TranslatorApiException implements Exception {
  const TranslatorApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class TranslatorApiClient {
  const TranslatorApiClient(this._dio);

  final Dio _dio;

  Future<PredictionResponseModel> predictFrame({
    required Uint8List bytes,
    required String filename,
  }) async {
    try {
      debugPrint(
        '[TranslatorApiClient] POST ${BackendConfig.predictPath} '
        'filename=$filename bytes=${bytes.length}',
      );

      final response = await _dio.post<Map<String, dynamic>>(
        BackendConfig.predictPath,
        data: FormData.fromMap({
          BackendConfig.frameFieldName: MultipartFile.fromBytes(
            bytes,
            filename: filename,
          ),
        }),
      );

      final data = response.data;
      if (data == null) {
        throw const FormatException('Prediction response was empty.');
      }

      debugPrint(
        '[TranslatorApiClient] POST ${BackendConfig.predictPath} '
        'completed with status ${response.statusCode}',
      );

      return PredictionResponseModel.fromJson(data);
    } on DioException catch (error) {
      debugPrint(
        '[TranslatorApiClient] POST ${BackendConfig.predictPath} failed: '
        'type=${error.type} message=${error.message} '
        'status=${error.response?.statusCode}',
      );
      throw TranslatorApiException(_messageForDioError(error));
    } on FormatException {
      rethrow;
    } catch (error) {
      throw TranslatorApiException('Prediction request failed: $error');
    }
  }

  String _messageForDioError(DioException error) {
    return switch (error.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        'Backend request timed out. Check that FastAPI is running.',
      DioExceptionType.connectionError =>
        'Could not connect to the backend. Check the backend URL and server.',
      DioExceptionType.badResponse =>
        'Backend returned ${error.response?.statusCode ?? 'an error'}.',
      DioExceptionType.cancel => 'Prediction request was cancelled.',
      _ => 'Backend request failed: ${error.message ?? 'unknown error'}.',
    };
  }
}
