class Prediction {
  const Prediction({
    required this.label,
    required this.confidence,
    required this.stable,
    required this.history,
  });

  final String label;
  final double confidence;
  final bool stable;
  final List<String> history;

  bool get hasLabel => label.trim().isNotEmpty;
}
