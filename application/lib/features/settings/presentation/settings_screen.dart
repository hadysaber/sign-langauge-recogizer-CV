import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/app_page.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/section_header.dart';
import '../../../shared/widgets/status_indicator.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppPage(
      title: 'Settings',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionHeader(
            title: 'Experience',
            subtitle: 'These controls are visual placeholders for now.',
          ),
          SizedBox(height: 14.h),
          const GlassCard(
            child: Column(
              children: [
                _SettingsSwitchRow(
                  icon: Icons.dark_mode_rounded,
                  title: 'Dark theme',
                  subtitle: 'Prepared for theme switching later.',
                  value: true,
                ),
                _Divider(),
                _SettingsRow(
                  icon: Icons.translate_rounded,
                  title: 'Language',
                  subtitle: 'English / Arabic support planned.',
                  trailing: Text('English'),
                ),
                _Divider(),
                _SettingsRow(
                  icon: Icons.speed_rounded,
                  title: 'Confidence threshold',
                  subtitle: 'Minimum confidence before accepting signs.',
                  trailing: Text('70%'),
                ),
              ],
            ),
          ).animate().fadeIn().slideY(begin: 0.08),
          SizedBox(height: 22.h),
          const SectionHeader(title: 'System status'),
          SizedBox(height: 14.h),
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const StatusIndicator(
                  label: 'Backend not connected',
                  color: AppColors.warning,
                ),
                SizedBox(height: 14.h),
                Text(
                  'The local FastAPI backend will be connected in the integration phase. Camera permissions and endpoint configuration will live here.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.textMutedOnDark,
                        height: 1.5,
                      ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 120.ms).slideY(begin: 0.08),
          SizedBox(height: 22.h),
          const SectionHeader(title: 'App information'),
          SizedBox(height: 14.h),
          const GlassCard(
            child: Column(
              children: [
                _SettingsRow(
                  icon: Icons.memory_rounded,
                  title: 'AI pipeline',
                  subtitle: 'MediaPipe landmarks plus LSTM classifier.',
                  trailing: Text('Ready'),
                ),
                _Divider(),
                _SettingsRow(
                  icon: Icons.mobile_friendly_rounded,
                  title: 'Mobile shell',
                  subtitle: 'Flutter UI foundation.',
                  trailing: Text('Phase 4'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsSwitchRow extends StatelessWidget {
  const _SettingsSwitchRow({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.value,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final bool value;

  @override
  Widget build(BuildContext context) {
    return _SettingsRow(
      icon: icon,
      title: title,
      subtitle: subtitle,
      trailing: Switch(value: value, onChanged: null),
    );
  }
}

class _SettingsRow extends StatelessWidget {
  const _SettingsRow({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.trailing,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final Widget trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 44.r,
          height: 44.r,
          decoration: BoxDecoration(
            color: AppColors.softBlue.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(14.r),
          ),
          child: Icon(icon, color: AppColors.softBlue, size: 22.r),
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
        SizedBox(width: 12.w),
        DefaultTextStyle(
          style: Theme.of(context).textTheme.labelLarge!.copyWith(
                color: AppColors.softBlue,
                fontWeight: FontWeight.w900,
              ),
          child: trailing,
        ),
      ],
    );
  }
}

class _Divider extends StatelessWidget {
  const _Divider();

  @override
  Widget build(BuildContext context) {
    return Divider(
      height: 30.h,
      color: AppColors.white.withValues(alpha: 0.08),
    );
  }
}
