class LatencySnapshot {
  const LatencySnapshot({
    this.vadMs = 0,
    this.sttMs = 0,
    this.translationMs = 0,
    this.ttsMs = 0,
    this.totalMs = 0,
  });

  final double vadMs;
  final double sttMs;
  final double translationMs;
  final double ttsMs;
  final double totalMs;
}
