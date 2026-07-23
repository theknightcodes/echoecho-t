import 'package:flutter_riverpod/flutter_riverpod.dart';

enum BluetoothConnectionState { disconnected, scanning, connected }

class BluetoothStatus {
  const BluetoothStatus({
    this.state = BluetoothConnectionState.disconnected,
    this.deviceName,
  });

  final BluetoothConnectionState state;
  final String? deviceName;
}

/// Placeholder provider. Native Bluetooth scanning/routing lands in
/// Milestone 2+ (see docs/PHASE2_PLAN.md); this just gives the UI a
/// stable shape to bind to today.
class BluetoothNotifier extends StateNotifier<BluetoothStatus> {
  BluetoothNotifier() : super(const BluetoothStatus());
}

final bluetoothProvider =
    StateNotifierProvider<BluetoothNotifier, BluetoothStatus>((ref) {
  return BluetoothNotifier();
});
