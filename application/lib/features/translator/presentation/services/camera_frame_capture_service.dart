import 'dart:typed_data';

import 'package:camera/camera.dart';

class CapturedCameraFrame {
  const CapturedCameraFrame({
    required this.bytes,
    required this.filename,
  });

  final Uint8List bytes;
  final String filename;
}

class CameraFrameCaptureService {
  Future<CapturedCameraFrame> capture(CameraController? controller) async {
    if (controller == null || !controller.value.isInitialized) {
      throw CameraException(
        'camera_unavailable',
        'Camera is not initialized.',
      );
    }
    if (controller.value.isPreviewPaused) {
      throw CameraException(
        'camera_paused',
        'Camera preview is paused.',
      );
    }
    if (controller.value.isTakingPicture) {
      throw CameraException(
        'camera_busy',
        'Camera is already capturing a frame.',
      );
    }

    final file = await controller.takePicture();
    final bytes = await file.readAsBytes();
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    return CapturedCameraFrame(
      bytes: bytes,
      filename: 'frame_$timestamp.jpg',
    );
  }
}
