import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../core/theme/app_colors.dart';
import 'glass_card.dart';

class AnimatedInfoCard extends StatelessWidget {
  const AnimatedInfoCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.delay = Duration.zero,
    super.key,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final Duration delay;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Row(
        children: [
          Container(
            width: 46.r,
            height: 46.r,
            decoration: BoxDecoration(
              color: AppColors.softBlue.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(15.r),
            ),
            child: Icon(icon, color: AppColors.softBlue, size: 24.r),
          ),
          SizedBox(width: 14.w),
          Expanded(
            child: Column(
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
                        height: 1.35,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: delay).slideY(begin: 0.10);
  }
}
