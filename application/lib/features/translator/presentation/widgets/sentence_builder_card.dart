import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/glass_card.dart';
import '../../../../shared/widgets/section_header.dart';

class SentenceBuilderCard extends StatelessWidget {
  const SentenceBuilderCard({
    required this.sentence,
    super.key,
  });

  final String sentence;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionHeader(
            title: 'Sentence builder',
            subtitle: 'Stable predictions are appended without duplicates.',
          ),
          SizedBox(height: 14.h),
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(16.r),
            decoration: BoxDecoration(
              color: AppColors.deepNavy.withValues(alpha: 0.55),
              borderRadius: BorderRadius.circular(18.r),
              border:
                  Border.all(color: AppColors.white.withValues(alpha: 0.08)),
            ),
            child: Text(
              sentence,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    height: 1.5,
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
