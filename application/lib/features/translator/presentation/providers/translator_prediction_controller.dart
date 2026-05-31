import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/backend_config.dart';
import '../../data/repositories/prediction_repository_impl.dart';
import '../../data/services/translator_api_client.dart';
import '../../domain/entities/prediction.dart';
import '../../domain/repositories/prediction_repository.dart';
import '../../domain/usecases/send_frame_for_prediction.dart';
import '../services/camera_frame_capture_service.dart';
import 'translator_camera_controller.dart';

enum PredictionRunStatus { idle, detecting, stopped, error }

enum BackendConnectionStatus { unknown, connecting, connected, unavailable }

class TranslatorPredictionState {
  const TranslatorPredictionState({
    required this.runStatus,
    required this.backendStatus,
    this.prediction,
    this.errorMessage,
    this.history = const [],
    this.sentenceWords = const [],
    this.isSending = false,
  });

  const TranslatorPredictionState.initial()
      : runStatus = PredictionRunStatus.idle,
        backendStatus = BackendConnectionStatus.unknown,
        prediction = null,
        errorMessage = null,
        history = const [],
        sentenceWords = const [],
        isSending = false;

  final PredictionRunStatus runStatus;
  final BackendConnectionStatus backendStatus;
  final Prediction? prediction;
  final String? errorMessage;
  final List<String> history;
  final List<String> sentenceWords;
  final bool isSending;

  bool get isDetecting => runStatus == PredictionRunStatus.detecting;
  bool get canStart => !isDetecting;
  bool get canStop => isDetecting;
  String get sentence => sentenceWords.isEmpty
      ? 'Stable signs will appear here.'
      : sentenceWords.join(' ');

  String get statusLabel {
    if (isSending) {
      return 'Sending frame';
    }
    return switch (runStatus) {
      PredictionRunStatus.idle => 'Backend idle',
      PredictionRunStatus.detecting => 'Detecting',
      PredictionRunStatus.stopped => 'Detection stopped',
      PredictionRunStatus.error => 'Backend error',
    };
  }

  TranslatorPredictionState copyWith({
    PredictionRunStatus? runStatus,
    BackendConnectionStatus? backendStatus,
    Prediction? prediction,
    String? errorMessage,
    List<String>? history,
    List<String>? sentenceWords,
    bool? isSending,
    bool clearError = false,
  }) {
    return TranslatorPredictionState(
      runStatus: runStatus ?? this.runStatus,
      backendStatus: backendStatus ?? this.backendStatus,
      prediction: prediction ?? this.prediction,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      history: history ?? this.history,
      sentenceWords: sentenceWords ?? this.sentenceWords,
      isSending: isSending ?? this.isSending,
    );
  }
}

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: BackendConfig.baseUrl,
      connectTimeout: BackendConfig.timeout,
      sendTimeout: BackendConfig.timeout,
      receiveTimeout: BackendConfig.timeout,
    ),
  );

  dio.interceptors.add(
    LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: false,
      responseHeader: false,
      responseBody: true,
      error: true,
      logPrint: (object) {
        debugPrint('[Dio /api/v1/predict] $object');
      },
    ),
  );

  return dio;
});

final translatorApiClientProvider = Provider<TranslatorApiClient>((ref) {
  return TranslatorApiClient(ref.watch(dioProvider));
});

final predictionRepositoryProvider = Provider<PredictionRepository>((ref) {
  return PredictionRepositoryImpl(ref.watch(translatorApiClientProvider));
});

final sendFrameForPredictionProvider = Provider<SendFrameForPrediction>((ref) {
  return SendFrameForPrediction(ref.watch(predictionRepositoryProvider));
});

final cameraFrameCaptureServiceProvider =
    Provider<CameraFrameCaptureService>((ref) {
  return CameraFrameCaptureService();
});

final translatorPredictionControllerProvider =
    StateNotifierProvider.autoDispose<TranslatorPredictionController,
        TranslatorPredictionState>((ref) {
  final captureService = ref.watch(cameraFrameCaptureServiceProvider);

  return TranslatorPredictionController(
    sendFrameForPrediction: ref.watch(sendFrameForPredictionProvider),
    captureFrame: () {
      final cameraState = ref.read(translatorCameraControllerProvider);
      return captureService.capture(cameraState.controller);
    },
  );
});

class TranslatorPredictionController
    extends StateNotifier<TranslatorPredictionState> {
  TranslatorPredictionController({
    required SendFrameForPrediction sendFrameForPrediction,
    required Future<CapturedCameraFrame> Function() captureFrame,
    Duration interval = BackendConfig.predictionInterval,
  })  : _sendFrameForPrediction = sendFrameForPrediction,
        _captureFrame = captureFrame,
        _interval = interval,
        super(const TranslatorPredictionState.initial());

  final SendFrameForPrediction _sendFrameForPrediction;
  final Future<CapturedCameraFrame> Function() _captureFrame;
  final Duration _interval;

  Timer? _timer;
  bool _requestInFlight = false;

  Future<void> startDetection() async {
    if (state.isDetecting) {
      return;
    }

    state = state.copyWith(
      runStatus: PredictionRunStatus.detecting,
      backendStatus: BackendConnectionStatus.connecting,
      clearError: true,
    );

    await _sendNextFrame();
    _timer = Timer.periodic(_interval, (_) => _sendNextFrame());
  }

  void stopDetection() {
    _timer?.cancel();
    _timer = null;
    _requestInFlight = false;
    state = state.copyWith(
      runStatus: PredictionRunStatus.stopped,
      isSending: false,
    );
  }

  void clearTranslation() {
    state = state.copyWith(
      prediction: const Prediction(
        label: '',
        confidence: 0,
        stable: false,
        history: [],
      ),
      history: const [],
      sentenceWords: const [],
      clearError: true,
    );
  }

  Future<void> _sendNextFrame() async {
    if (_requestInFlight || !state.isDetecting) {
      return;
    }

    _requestInFlight = true;
    state = state.copyWith(isSending: true, clearError: true);

    try {
      final frame = await _captureFrame();
      debugPrint(
        '[PredictionController] Sending ${frame.bytes.length} bytes '
        'as ${frame.filename} to ${BackendConfig.baseUrl}'
        '${BackendConfig.predictPath}',
      );

      final prediction = await _sendFrameForPrediction(
        bytes: frame.bytes,
        filename: frame.filename,
      );

      debugPrint(
        '[PredictionController] Received prediction '
        'label="${prediction.label}" confidence=${prediction.confidence} '
        'stable=${prediction.stable}',
      );

      if (!mounted) {
        return;
      }

      state = state.copyWith(
        runStatus: PredictionRunStatus.detecting,
        backendStatus: BackendConnectionStatus.connected,
        prediction: prediction,
        history: prediction.history,
        sentenceWords: _nextSentenceWords(prediction),
        isSending: false,
        clearError: true,
      );
    } catch (error) {
      if (!mounted) {
        return;
      }
      debugPrint('[PredictionController] Prediction request failed: $error');
      _timer?.cancel();
      _timer = null;
      state = state.copyWith(
        runStatus: PredictionRunStatus.error,
        backendStatus: BackendConnectionStatus.unavailable,
        errorMessage: _messageForError(error),
        isSending: false,
      );
    } finally {
      _requestInFlight = false;
    }
  }

  List<String> _nextSentenceWords(Prediction prediction) {
    if (!prediction.stable || !prediction.hasLabel) {
      return state.sentenceWords;
    }
    if (state.sentenceWords.isNotEmpty &&
        state.sentenceWords.last == prediction.label) {
      return state.sentenceWords;
    }
    return [...state.sentenceWords, prediction.label];
  }

  String _messageForError(Object error) {
    final message = error.toString();
    if (message.contains('camera_unavailable') ||
        message.contains('Camera is not initialized')) {
      return 'Camera is unavailable. Allow permission and start the camera.';
    }
    if (message.contains('camera_paused')) {
      return 'Camera preview is paused. Start the camera before detection.';
    }
    if (error is FormatException) {
      return 'Backend returned an invalid prediction response.';
    }
    return message.replaceFirst('Exception: ', '');
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
