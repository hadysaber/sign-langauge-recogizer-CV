import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/app_page.dart';
import '../../../shared/widgets/section_header.dart';
import '../../../shared/widgets/status_indicator.dart';
import '../../../shared/widgets/translation_result_card.dart';
import 'providers/translator_camera_controller.dart';
import 'providers/translator_prediction_controller.dart';
import 'widgets/detection_controls.dart';
import 'widgets/detection_history.dart';
import 'widgets/live_camera_preview.dart';
import 'widgets/sentence_builder_card.dart';

class TranslatorScreen extends ConsumerStatefulWidget {
  const TranslatorScreen({super.key});

  @override
  ConsumerState<TranslatorScreen> createState() => _TranslatorScreenState();
}

class _TranslatorScreenState extends ConsumerState<TranslatorScreen>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(translatorCameraControllerProvider.notifier).initialize();
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final cameraController =
        ref.read(translatorCameraControllerProvider.notifier);
    final predictionController =
        ref.read(translatorPredictionControllerProvider.notifier);

    switch (state) {
      case AppLifecycleState.resumed:
        cameraController.resumeForLifecycle();
      case AppLifecycleState.inactive:
      case AppLifecycleState.hidden:
      case AppLifecycleState.paused:
      case AppLifecycleState.detached:
        predictionController.stopDetection();
        cameraController.pauseForLifecycle();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cameraState = ref.watch(translatorCameraControllerProvider);
    final predictionState = ref.watch(translatorPredictionControllerProvider);
    final cameraController =
        ref.read(translatorCameraControllerProvider.notifier);
    final predictionController =
        ref.read(translatorPredictionControllerProvider.notifier);
    final prediction = predictionState.prediction;

    return AppPage(
      title: 'Translator',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: SectionHeader(
                  title: 'Live workspace',
                  subtitle:
                      'Live camera frames are sent to the local AI backend.',
                ),
              ),
              StatusIndicator(
                label: predictionState.statusLabel,
                color: _predictionStatusColor(predictionState),
                pulsing: predictionState.isDetecting,
              ),
            ],
          ),
          SizedBox(height: 16.h),
          LiveCameraPreview(
            cameraState: cameraState,
            onRetry: cameraController.startPreview,
          ).animate().fadeIn().slideY(begin: 0.06),
          SizedBox(height: 18.h),
          TranslationResultCard(
            label: prediction?.hasLabel == true
                ? prediction!.label
                : predictionState.runStatus == PredictionRunStatus.error
                    ? 'Backend unavailable'
                    : 'Waiting for prediction',
            confidence: prediction?.confidence ?? 0,
            isStable: prediction?.stable ?? false,
          ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.06),
          SizedBox(height: 18.h),
          SentenceBuilderCard(
            sentence: predictionState.sentence,
          ).animate().fadeIn(delay: 180.ms).slideY(begin: 0.06),
          SizedBox(height: 18.h),
          DetectionHistory(items: predictionState.history)
              .animate()
              .fadeIn(delay: 260.ms)
              .slideY(begin: 0.06),
          SizedBox(height: 18.h),
          DetectionControls(
            canStart: predictionState.canStart &&
                cameraState.status != TranslatorCameraStatus.loading,
            canStop: cameraState.canStop || predictionState.canStop,
            onStart: () async {
              await cameraController.startPreview();
              final latestCameraState =
                  ref.read(translatorCameraControllerProvider);
              if (latestCameraState.status == TranslatorCameraStatus.ready) {
                await predictionController.startDetection();
              }
            },
            onStop: () {
              predictionController.stopDetection();
              cameraController.stopPreview();
            },
            onClear: predictionController.clearTranslation,
          ).animate().fadeIn(delay: 340.ms).slideY(begin: 0.06),
        ],
      ),
    );
  }

  Color _predictionStatusColor(TranslatorPredictionState state) {
    if (state.backendStatus == BackendConnectionStatus.connected) {
      return state.prediction?.stable == true
          ? AppColors.success
          : AppColors.softBlue;
    }
    return switch (state.backendStatus) {
      BackendConnectionStatus.unknown => AppColors.textMutedOnDark,
      BackendConnectionStatus.connecting => AppColors.softBlue,
      BackendConnectionStatus.connected => AppColors.success,
      BackendConnectionStatus.unavailable => AppColors.danger,
    };
  }
}
