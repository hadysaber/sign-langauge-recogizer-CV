import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../core/theme/app_colors.dart';

class StatusIndicator extends StatelessWidget {
  const StatusIndicator({
    required this.label,
    required this.color,
    this.pulsing = false,
    super.key,
  });

  final String label;
  final Color color;
  final bool pulsing;

  @override
  Widget build(BuildContext context) {
    final dot = Container(
      width: 9.r,
      height: 9.r,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.55),
            blurRadius: 14,
            spreadRadius: 2,
          ),
        ],
      ),
    );

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
      decoration: BoxDecoration(
        color: AppColors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.28)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          pulsing
              ? dot.animate(onPlay: (controller) => controller.repeat()).scale(
                    begin: const Offset(0.82, 0.82),
                    end: const Offset(1.18, 1.18),
                    duration: 900.ms,
                  )
              : dot,
          SizedBox(width: 8.w),
          Text(
            label,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: AppColors.textOnDark,
                  fontWeight: FontWeight.w800,
                ),
          ),
        ],
      ),
    );
  }
}
