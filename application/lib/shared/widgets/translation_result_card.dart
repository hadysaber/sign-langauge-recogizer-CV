import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../core/theme/app_colors.dart';
import 'glass_card.dart';
import 'status_indicator.dart';

class TranslationResultCard extends StatelessWidget {
  const TranslationResultCard({
    required this.label,
    required this.confidence,
    required this.isStable,
    super.key,
  });

  final String label;
  final double confidence;
  final bool isStable;

  @override
  Widget build(BuildContext context) {
    final percent = (confidence * 100).round();

    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Translation result',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.textMutedOnDark,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              StatusIndicator(
                label: isStable ? 'Stable' : 'Learning',
                color: isStable ? AppColors.success : AppColors.warning,
              ),
            ],
          ),
          SizedBox(height: 16.h),
          Text(
            label,
            style: Theme.of(context).textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0,
                ),
          ),
          SizedBox(height: 16.h),
          Row(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: LinearProgressIndicator(
                    value: confidence,
                    minHeight: 10.h,
                    backgroundColor: AppColors.white.withValues(alpha: 0.10),
                    valueColor:
                        const AlwaysStoppedAnimation(AppColors.softBlue),
                  ),
                ),
              ),
              SizedBox(width: 12.w),
              Text(
                '$percent%',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: AppColors.softBlue,
                      fontWeight: FontWeight.w900,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
