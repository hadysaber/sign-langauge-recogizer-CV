import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/glass_card.dart';
import '../../../../shared/widgets/section_header.dart';

class DetectionHistory extends StatelessWidget {
  const DetectionHistory({
    required this.items,
    super.key,
  });

  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionHeader(
            title: 'Detected history',
            subtitle: 'Stable signs from the current detection session.',
          ),
          SizedBox(height: 14.h),
          if (items.isEmpty)
            Text(
              'No stable signs detected yet.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textMutedOnDark,
                  ),
            )
          else
            Wrap(
              spacing: 8.w,
              runSpacing: 8.h,
              children: items
                  .map(
                    (item) => Chip(
                      label: Text(item),
                      backgroundColor:
                          AppColors.softBlue.withValues(alpha: 0.12),
                      side: BorderSide(
                        color: AppColors.softBlue.withValues(alpha: 0.22),
                      ),
                      labelStyle:
                          Theme.of(context).textTheme.labelLarge?.copyWith(
                                color: AppColors.textOnDark,
                                fontWeight: FontWeight.w800,
                              ),
                    ),
                  )
                  .toList(),
            ),
        ],
      ),
    );
  }
}
