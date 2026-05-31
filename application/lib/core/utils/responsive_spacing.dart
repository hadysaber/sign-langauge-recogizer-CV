import 'package:flutter/widgets.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

abstract final class ResponsiveSpacing {
  static double pageHorizontal(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    if (width >= 700) {
      return 32.w;
    }
    return 20.w;
  }
}
