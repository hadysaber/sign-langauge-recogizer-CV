import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../../../shared/widgets/status_indicator.dart';
import '../providers/translator_camera_controller.dart';

class LiveCameraPreview extends StatelessWidget {
  const LiveCameraPreview({
    required this.cameraState,
    required this.onRetry,
    super.key,
  });

  final TranslatorCameraState cameraState;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final color = _statusColor(cameraState.status);

    return AspectRatio(
      aspectRatio: 3 / 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(28.r),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF101B31),
              Color(0xFF0C1425),
              Color(0xFF050A14),
            ],
          ),
          border: Border.all(color: AppColors.white.withValues(alpha: 0.10)),
        ),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          children: [
            Positioned.fill(
              child: _CameraSurface(
                cameraState: cameraState,
                onRetry: onRetry,
              ),
            ),
            if (cameraState.status == TranslatorCameraStatus.ready)
              const Positioned.fill(child: _ScanningOverlay()),
            Positioned(
              left: 18.w,
              top: 18.h,
              child: StatusIndicator(
                label: cameraState.statusLabel,
                color: color,
                pulsing: cameraState.status == TranslatorCameraStatus.ready ||
                    cameraState.status == TranslatorCameraStatus.loading,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _statusColor(TranslatorCameraStatus status) {
    return switch (status) {
      TranslatorCameraStatus.ready => AppColors.success,
      TranslatorCameraStatus.loading => AppColors.softBlue,
      TranslatorCameraStatus.stopped => AppColors.warning,
      TranslatorCameraStatus.permissionDenied => AppColors.warning,
      TranslatorCameraStatus.noCamera => AppColors.warning,
      TranslatorCameraStatus.failure => AppColors.danger,
      TranslatorCameraStatus.initial => AppColors.textMutedOnDark,
    };
  }
}

class _CameraSurface extends StatelessWidget {
  const _CameraSurface({
    required this.cameraState,
    required this.onRetry,
  });

  final TranslatorCameraState cameraState;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    if (cameraState.status == TranslatorCameraStatus.ready &&
        cameraState.hasInitializedPreview) {
      return _CameraPreview(controller: cameraState.controller!);
    }

    if (cameraState.status == TranslatorCameraStatus.stopped &&
        cameraState.hasInitializedPreview) {
      return Stack(
        fit: StackFit.expand,
        children: [
          _CameraPreview(controller: cameraState.controller!),
          ColoredBox(color: Colors.black.withValues(alpha: 0.48)),
          _CameraMessage(
            icon: Icons.pause_circle_filled_rounded,
            title: 'Camera paused',
            message: cameraState.message ?? 'Press Start to resume preview.',
            actionLabel: 'Resume preview',
            onAction: onRetry,
          ),
        ],
      );
    }

    if (cameraState.status == TranslatorCameraStatus.loading) {
      return const _CameraLoading();
    }

    return _CameraMessage(
      icon: _messageIcon(cameraState.status),
      title: _messageTitle(cameraState.status),
      message: cameraState.message ?? 'Start the camera to begin live preview.',
      actionLabel: 'Try again',
      onAction: onRetry,
    );
  }

  IconData _messageIcon(TranslatorCameraStatus status) {
    return switch (status) {
      TranslatorCameraStatus.permissionDenied => Icons.videocam_off_rounded,
      TranslatorCameraStatus.noCamera => Icons.no_photography_rounded,
      TranslatorCameraStatus.failure => Icons.error_rounded,
      _ => Icons.videocam_rounded,
    };
  }

  String _messageTitle(TranslatorCameraStatus status) {
    return switch (status) {
      TranslatorCameraStatus.permissionDenied => 'Camera permission needed',
      TranslatorCameraStatus.noCamera => 'No camera found',
      TranslatorCameraStatus.failure => 'Could not open camera',
      TranslatorCameraStatus.initial => 'Camera ready to start',
      _ => 'Camera unavailable',
    };
  }
}

class _CameraPreview extends StatelessWidget {
  const _CameraPreview({required this.controller});

  final CameraController controller;

  @override
  Widget build(BuildContext context) {
    return FittedBox(
      fit: BoxFit.cover,
      child: SizedBox(
        width: controller.value.previewSize?.height ?? 1,
        height: controller.value.previewSize?.width ?? 1,
        child: CameraPreview(controller),
      ),
    );
  }
}

class _CameraLoading extends StatelessWidget {
  const _CameraLoading();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(child: CustomPaint(painter: _GridPainter())),
        Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 52.r,
                height: 52.r,
                child: const CircularProgressIndicator(
                  strokeWidth: 3,
                  color: AppColors.softBlue,
                ),
              ),
              SizedBox(height: 18.h),
              Text(
                'Opening camera',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: AppColors.textOnDark,
                      fontWeight: FontWeight.w800,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CameraMessage extends StatelessWidget {
  const _CameraMessage({
    required this.icon,
    required this.title,
    required this.message,
    required this.actionLabel,
    required this.onAction,
  });

  final IconData icon;
  final String title;
  final String message;
  final String actionLabel;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(child: CustomPaint(painter: _GridPainter())),
        Center(
          child: Padding(
            padding: EdgeInsets.all(28.r),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 96.r,
                  height: 96.r,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.softBlue.withValues(alpha: 0.14),
                    border: Border.all(
                      color: AppColors.softBlue.withValues(alpha: 0.28),
                    ),
                  ),
                  child: Icon(icon, color: AppColors.softBlue, size: 44.r),
                ),
                SizedBox(height: 18.h),
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: AppColors.textOnDark,
                        fontWeight: FontWeight.w900,
                      ),
                ),
                SizedBox(height: 8.h),
                Text(
                  message,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.textMutedOnDark,
                        height: 1.45,
                      ),
                ),
                SizedBox(height: 18.h),
                AppButton(
                  label: actionLabel,
                  icon: Icons.refresh_rounded,
                  onPressed: onAction,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _ScanningOverlay extends StatelessWidget {
  const _ScanningOverlay();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Container(
          height: 3.h,
          margin: EdgeInsets.symmetric(horizontal: 22.w),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            gradient: LinearGradient(
              colors: [
                Colors.transparent,
                AppColors.cyan.withValues(alpha: 0.95),
                Colors.transparent,
              ],
            ),
          ),
        ).animate(onPlay: (controller) => controller.repeat()).moveY(
              begin: 72.h,
              end: constraints.maxHeight - 72.h,
              duration: 2100.ms,
              curve: Curves.easeInOut,
            );
      },
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.white.withValues(alpha: 0.045)
      ..strokeWidth = 1;

    for (var x = 0.0; x < size.width; x += 36) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (var y = 0.0; y < size.height; y += 36) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
