import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/animated_info_card.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_page.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/section_header.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppPage(
      title: 'Home',
      actions: [
        IconButton(
          onPressed: () => context.go(AppRoutes.settings),
          icon: const Icon(Icons.settings_rounded),
        ),
      ],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _HeroSection(onStart: () => context.go(AppRoutes.translator)),
          SizedBox(height: 26.h),
          const SectionHeader(
            title: 'Quick actions',
            subtitle:
                'Everything is staged for camera and backend integration.',
          ),
          SizedBox(height: 14.h),
          _QuickActionGrid(
            onTranslator: () => context.go(AppRoutes.translator),
            onSettings: () => context.go(AppRoutes.settings),
            onAbout: () => context.go(AppRoutes.about),
          ),
          SizedBox(height: 26.h),
          const SectionHeader(title: 'Built for accessibility'),
          SizedBox(height: 14.h),
          const AnimatedInfoCard(
            icon: Icons.visibility_rounded,
            title: 'Clear visual feedback',
            subtitle: 'Large labels, confidence states, and readable contrast.',
          ),
          SizedBox(height: 12.h),
          const AnimatedInfoCard(
            icon: Icons.translate_rounded,
            title: 'Language ready',
            subtitle:
                'Prepared for English and Arabic support in future phases.',
            delay: Duration(milliseconds: 100),
          ),
          SizedBox(height: 12.h),
          const AnimatedInfoCard(
            icon: Icons.bolt_rounded,
            title: 'Fast AI workflow',
            subtitle:
                'The next phase will stream frames to the local AI backend.',
            delay: Duration(milliseconds: 180),
          ),
        ],
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  const _HeroSection({required this.onStart});

  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: EdgeInsets.all(22.r),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
            decoration: BoxDecoration(
              color: AppColors.softBlue.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Text(
              'Live sign translation',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.cyan,
                    fontWeight: FontWeight.w900,
                  ),
            ),
          ),
          SizedBox(height: 18.h),
          Text(
            'Make every sign easier to understand.',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w900,
                  height: 1.08,
                  letterSpacing: 0,
                ),
          ),
          SizedBox(height: 14.h),
          Text(
            'A clean translator experience designed for camera input, stable AI predictions, and readable sentence output.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textMutedOnDark,
                  height: 1.55,
                ),
          ),
          SizedBox(height: 22.h),
          AppButton(
            label: 'Start translating',
            icon: Icons.play_arrow_rounded,
            onPressed: onStart,
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.08);
  }
}

class _QuickActionGrid extends StatelessWidget {
  const _QuickActionGrid({
    required this.onTranslator,
    required this.onSettings,
    required this.onAbout,
  });

  final VoidCallback onTranslator;
  final VoidCallback onSettings;
  final VoidCallback onAbout;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 520;
        return GridView.count(
          crossAxisCount: isWide ? 3 : 1,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12.h,
          crossAxisSpacing: 12.w,
          childAspectRatio: isWide ? 1.05 : 3.7,
          children: [
            _ActionCard(
              icon: Icons.videocam_rounded,
              title: 'Translator',
              subtitle: 'Open live workspace',
              onTap: onTranslator,
            ),
            _ActionCard(
              icon: Icons.tune_rounded,
              title: 'Settings',
              subtitle: 'Prepare thresholds',
              onTap: onSettings,
            ),
            _ActionCard(
              icon: Icons.info_rounded,
              title: 'About',
              subtitle: 'Project overview',
              onTap: onAbout,
            ),
          ],
        );
      },
    );
  }
}

class _ActionCard extends StatelessWidget {
  const _ActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(22.r),
      onTap: onTap,
      child: GlassCard(
        child: Row(
          children: [
            Icon(icon, color: AppColors.softBlue, size: 28.r),
            SizedBox(width: 14.w),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppColors.textMutedOnDark,
                        ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded),
          ],
        ),
      ),
    );
  }
}
