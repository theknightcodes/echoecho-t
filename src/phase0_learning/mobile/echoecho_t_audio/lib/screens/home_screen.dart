import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

/// Simple audio recorder screen for Phase 0 learning.
/// Demonstrates: permissions, recording, playback, file management.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  bool _isRecording = false;
  bool _isPlaying = false;
  String? _recordingPath;
  String _status = 'Ready';

  @override
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    super.dispose();
  }

  Future<void> _requestPermission() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      setState(() => _status = 'Microphone permission denied');
    }
  }

  Future<void> _startRecording() async {
    await _requestPermission();

    if (!await _recorder.hasPermission()) {
      setState(() => _status = 'No mic permission');
      return;
    }

    final dir = await getApplicationDocumentsDirectory();
    final path = '${dir.path}/echoecho_test_${DateTime.now().millisecondsSinceEpoch}.m4a';

    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.aacLc,
        sampleRate: 16000,
        numChannels: 1,
      ),
      path: path,
    );

    setState(() {
      _isRecording = true;
      _recordingPath = path;
      _status = 'Recording...';
    });
  }

  Future<void> _stopRecording() async {
    await _recorder.stop();
    setState(() {
      _isRecording = false;
      _status = 'Recorded: ${_recordingPath?.split('/').last}';
    });
  }

  Future<void> _playRecording() async {
    if (_recordingPath == null) return;

    await _player.play(DeviceFileSource(_recordingPath!));
    setState(() => _isPlaying = true);

    _player.onPlayerComplete.listen((_) {
      setState(() => _isPlaying = false);
    });
  }

  Future<void> _stopPlayback() async {
    await _player.stop();
    setState(() => _isPlaying = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('EchoEcho-T Audio Test'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _status,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              // Recording button
              ElevatedButton.icon(
                onPressed: _isRecording ? _stopRecording : _startRecording,
                icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                label: Text(_isRecording ? 'Stop Recording' : 'Start Recording'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isRecording ? Colors.red : Colors.deepPurple,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
              ),
              const SizedBox(height: 16),
              // Playback button
              if (_recordingPath != null)
                ElevatedButton.icon(
                  onPressed: _isPlaying ? _stopPlayback : _playRecording,
                  icon: Icon(_isPlaying ? Icons.stop : Icons.play_arrow),
                  label: Text(_isPlaying ? 'Stop Playback' : 'Play Recording'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  ),
                ),
              const SizedBox(height: 32),
              // Info
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Audio Config', style: Theme.of(context).textTheme.titleSmall),
                    const SizedBox(height: 8),
                    const Text('Sample Rate: 16kHz'),
                    const Text('Channels: 1 (mono)'),
                    const Text('Encoder: AAC-LC'),
                    const Text('Format: .m4a'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
