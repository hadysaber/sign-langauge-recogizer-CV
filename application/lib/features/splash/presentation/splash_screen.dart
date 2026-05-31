import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_strings.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/glass_card.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment.topRight,
            radius: 1.2,
            colors: [
              Color(0xFF153E66),
              AppColors.navy,
              AppColors.deepNavy,
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: EdgeInsets.all(24.r),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Align(
                  alignment: Alignment.topRight,
                  child: GlassCard(
                    padding: EdgeInsets.symmetric(
                      horizontal: 12.w,
                      vertical: 8.h,
                    ),
                    child: Text(
                      'AI powered',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: AppColors.textOnDark,
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                  ),
                ).animate().fadeIn().slideX(begin: 0.08),
                const Spacer(),
                _AnimatedLogo()
                    .animate(
                        onPlay: (controller) =>
                            controller.repeat(reverse: true))
                    .moveY(begin: 0, end: -8, duration: 1800.ms),
                SizedBox(height: 30.h),
                Text(
                  AppStrings.appName,
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.w900,
                        height: 1.02,
                        letterSpacing: 0,
                      ),
                ).animate().fadeIn(delay: 180.ms).slideY(begin: 0.10),
                SizedBox(height: 14.h),
                Text(
                  'A polished mobile experience for accessible, real-time sign translation.',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.textMutedOnDark,
                        height: 1.55,
                      ),
                ).animate().fadeIn(delay: 280.ms).slideY(begin: 0.08),
                SizedBox(height: 28.h),
                ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: LinearProgressIndicator(
                    minHeight: 6.h,
                    value: 0.72,
                    backgroundColor: AppColors.white.withValues(alpha: 0.10),
                    valueColor:
                        const AlwaysStoppedAnimation(AppColors.softBlue),
                  ),
                ).animate().fadeIn(delay: 380.ms),
                const Spacer(),
                AppButton(
                  label: 'Enter translator',
                  icon: Icons.arrow_forward_rounded,
                  onPressed: () => context.go(AppRoutes.home),
                ).animate().fadeIn(delay: 480.ms).slideY(begin: 0.12),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _AnimatedLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 96.r,
      height: 96.r,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28.r),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppColors.softBlue, AppColors.cyan],
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.softBlue.withValues(alpha: 0.45),
            blurRadius: 40,
            offset: const Offset(0, 18),
          ),
        ],
      ),
      child: Icon(
        Icons.sign_language_rounded,
        color: AppColors.deepNavy,
        size: 52.r,
      ),
    ).animate().scale(duration: 520.ms, curve: Curves.easeOutBack).fadeIn();
  }
}
