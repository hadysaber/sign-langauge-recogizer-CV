import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../core/constants/app_strings.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/animated_info_card.dart';
import '../../../shared/widgets/app_page.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/section_header.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppPage(
      title: 'About',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.sign_language_rounded,
                  color: AppColors.softBlue,
                  size: 42.r,
                ),
                SizedBox(height: 16.h),
                Text(
                  AppStrings.appName,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0,
                      ),
                ),
                SizedBox(height: 12.h),
                Text(
                  'A portfolio-grade mobile app concept that translates sign gestures into clear text using a local AI recognition backend.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.textMutedOnDark,
                        height: 1.6,
                      ),
                ),
              ],
            ),
          ).animate().fadeIn().slideY(begin: 0.08),
          SizedBox(height: 24.h),
          const SectionHeader(
            title: 'Technology stack',
            subtitle:
                'The UI is ready before camera and inference phases begin.',
          ),
          SizedBox(height: 14.h),
          const AnimatedInfoCard(
            icon: Icons.flutter_dash_rounded,
            title: 'Flutter',
            subtitle: 'Cross-platform mobile UI with responsive layout.',
          ),
          SizedBox(height: 12.h),
          const AnimatedInfoCard(
            icon: Icons.api_rounded,
            title: 'FastAPI backend',
            subtitle:
                'Planned local bridge to the existing Python AI pipeline.',
            delay: Duration(milliseconds: 100),
          ),
          SizedBox(height: 12.h),
          const AnimatedInfoCard(
            icon: Icons.psychology_rounded,
            title: 'MediaPipe + LSTM',
            subtitle: 'Landmark sequence recognition for sign classification.',
            delay: Duration(milliseconds: 180),
          ),
          SizedBox(height: 24.h),
          const SectionHeader(title: 'Project goals'),
          SizedBox(height: 14.h),
          const GlassCard(
            child: Column(
              children: [
                _GoalItem('Create a clean accessible translation experience.'),
                _GoalItem(
                    'Support stable predictions with confidence feedback.'),
                _GoalItem('Prepare for Arabic and English language modes.'),
                _GoalItem('Keep the AI and mobile app cleanly separated.'),
              ],
            ),
          ),
          SizedBox(height: 24.h),
          GlassCard(
            child: Text(
              'Credits: built as a sign language recognition and translation project using Flutter, MediaPipe, TensorFlow/Keras, and FastAPI.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textMutedOnDark,
                    height: 1.55,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GoalItem extends StatelessWidget {
  const _GoalItem(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8.h),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.check_circle_rounded,
              color: AppColors.success, size: 20.r),
          SizedBox(width: 10.w),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    height: 1.4,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
