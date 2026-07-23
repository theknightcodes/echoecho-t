import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bluetooth_provider.dart';

class BluetoothDevicePicker extends ConsumerWidget {
  const BluetoothDevicePicker({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bluetooth = ref.watch(bluetoothProvider);
    return ListTile(
      leading: const Icon(Icons.bluetooth),
      title: Text(bluetooth.deviceName ?? 'No device connected'),
      subtitle: Text(bluetooth.state.name),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        // Native BLE scan/connect lands in Milestone 2.
      },
    );
  }
}
