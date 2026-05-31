import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../../shared/widgets/app_button.dart';

class DetectionControls extends StatelessWidget {
  const DetectionControls({
    required this.onStart,
    required this.onStop,
    required this.onClear,
    this.canStart = true,
    this.canStop = true,
    super.key,
  });

  final VoidCallback onStart;
  final VoidCallback onStop;
  final VoidCallback onClear;
  final bool canStart;
  final bool canStop;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: AppButton(
                label: 'Start',
                icon: Icons.play_arrow_rounded,
                onPressed: canStart ? onStart : null,
              ),
            ),
            SizedBox(width: 12.w),
            Expanded(
              child: AppButton(
                label: 'Stop',
                icon: Icons.stop_rounded,
                variant: AppButtonVariant.secondary,
                onPressed: canStop ? onStop : null,
              ),
            ),
          ],
        ),
        SizedBox(height: 12.h),
        AppButton(
          label: 'Clear translation',
          icon: Icons.cleaning_services_rounded,
          variant: AppButtonVariant.secondary,
          onPressed: onClear,
        ),
      ],
    );
  }
}
