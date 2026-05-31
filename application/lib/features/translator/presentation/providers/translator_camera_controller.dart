import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

enum TranslatorCameraStatus {
  initial,
  loading,
  ready,
  stopped,
  permissionDenied,
  noCamera,
  failure,
}

class TranslatorCameraState {
  const TranslatorCameraState({
    required this.status,
    this.controller,
    this.message,
  });

  const TranslatorCameraState.initial()
      : status = TranslatorCameraStatus.initial,
        controller = null,
        message = null;

  final TranslatorCameraStatus status;
  final CameraController? controller;
  final String? message;

  bool get hasInitializedPreview =>
      controller != null && controller!.value.isInitialized;

  bool get canStart =>
      status == TranslatorCameraStatus.stopped ||
      status == TranslatorCameraStatus.failure ||
      status == TranslatorCameraStatus.initial ||
      status == TranslatorCameraStatus.permissionDenied;

  bool get canStop => status == TranslatorCameraStatus.ready;

  String get statusLabel {
    return switch (status) {
      TranslatorCameraStatus.initial => 'Camera idle',
      TranslatorCameraStatus.loading => 'Opening camera',
      TranslatorCameraStatus.ready => 'Camera live',
      TranslatorCameraStatus.stopped => 'Camera paused',
      TranslatorCameraStatus.permissionDenied => 'Permission needed',
      TranslatorCameraStatus.noCamera => 'No camera',
      TranslatorCameraStatus.failure => 'Camera error',
    };
  }
}

final translatorCameraControllerProvider = StateNotifierProvider.autoDispose<
    TranslatorCameraController, TranslatorCameraState>((ref) {
  return TranslatorCameraController();
});

class TranslatorCameraController extends StateNotifier<TranslatorCameraState> {
  TranslatorCameraController() : super(const TranslatorCameraState.initial());

  CameraController? _controller;
  List<CameraDescription> _cameras = const [];

  Future<void> initialize() async {
    if (state.status == TranslatorCameraStatus.loading) {
      return;
    }

    state = TranslatorCameraState(
      status: TranslatorCameraStatus.loading,
      controller: _controller,
    );

    try {
      final permissionStatus = await Permission.camera.request();
      if (!permissionStatus.isGranted) {
        state = const TranslatorCameraState(
          status: TranslatorCameraStatus.permissionDenied,
          message: 'Camera permission is required to show live translation.',
        );
        return;
      }

      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        state = const TranslatorCameraState(
          status: TranslatorCameraStatus.noCamera,
          message: 'No camera was found on this device.',
        );
        return;
      }

      final selectedCamera = _selectCamera(_cameras);
      await _disposeCurrentController();

      final controller = CameraController(
        selectedCamera,
        ResolutionPreset.medium,
        enableAudio: false,
      );
      _controller = controller;

      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }

      state = TranslatorCameraState(
        status: TranslatorCameraStatus.ready,
        controller: controller,
      );
    } on CameraException catch (error) {
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.failure,
        message: error.description ?? error.code,
      );
    } catch (error) {
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.failure,
        message: error.toString(),
      );
    }
  }

  Future<void> startPreview() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) {
      await initialize();
      return;
    }

    try {
      if (controller.value.isPreviewPaused) {
        await controller.resumePreview();
      }
      if (!mounted) {
        return;
      }
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.ready,
        controller: controller,
      );
    } catch (error) {
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.failure,
        controller: controller,
        message: error.toString(),
      );
    }
  }

  Future<void> stopPreview() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) {
      state = const TranslatorCameraState.initial();
      return;
    }

    try {
      if (!controller.value.isPreviewPaused) {
        await controller.pausePreview();
      }
      if (!mounted) {
        return;
      }
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.stopped,
        controller: controller,
        message: 'Camera preview is paused. Press Start to resume.',
      );
    } catch (error) {
      state = TranslatorCameraState(
        status: TranslatorCameraStatus.failure,
        controller: controller,
        message: error.toString(),
      );
    }
  }

  Future<void> pauseForLifecycle() async {
    if (state.status != TranslatorCameraStatus.ready) {
      return;
    }
    await stopPreview();
  }

  Future<void> resumeForLifecycle() async {
    if (state.status != TranslatorCameraStatus.stopped) {
      return;
    }
    await startPreview();
  }

  CameraDescription _selectCamera(List<CameraDescription> cameras) {
    return cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front,
      orElse: () => cameras.first,
    );
  }

  Future<void> _disposeCurrentController() async {
    final controller = _controller;
    _controller = null;
    if (controller != null) {
      await controller.dispose();
    }
  }

  @override
  void dispose() {
    unawaited(_disposeCurrentController());
    super.dispose();
  }
}
