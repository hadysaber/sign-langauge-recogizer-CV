import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../core/utils/responsive_spacing.dart';

class AppPage extends StatelessWidget {
  const AppPage({
    required this.title,
    required this.child,
    this.actions,
    this.showAppBar = true,
    super.key,
  });

  final String title;
  final Widget child;
  final List<Widget>? actions;
  final bool showAppBar;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: showAppBar
          ? AppBar(
              title: Text(title),
              actions: actions,
            )
          : null,
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF0B1220),
              Color(0xFF07101F),
              Color(0xFF050A14),
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.fromLTRB(
              ResponsiveSpacing.pageHorizontal(context),
              showAppBar ? 12.h : 20.h,
              ResponsiveSpacing.pageHorizontal(context),
              28.h,
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}
