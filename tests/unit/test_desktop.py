"""Deterministic regression tests: no microphone, model downloads or cloud calls."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src/phase1_desktop'))
from audio.capture import AudioCapture
from audio.playback import AudioPlayback
from ai.language_manager import LanguageManager
from ai.tts import TTS, _sanitize_for_tts
from pipeline.orchestrator_v2 import Pipeline


class AudioTests(unittest.TestCase):
    def test_playback_preserves_tail_and_pads_silence(self):
        player = AudioPlayback(block_size=4)
        audio = np.arange(6, dtype=np.float32)
        self.assertTrue(player.play(audio))
        audio[:] = 99  # Caller mutation must not alter queued samples.
        out = np.empty((4, 1), dtype=np.float32)
        player._callback(out, 4, None, None)
        np.testing.assert_array_equal(out[:, 0], [0, 1, 2, 3])
        player._callback(out, 4, None, None)
        np.testing.assert_array_equal(out[:, 0], [4, 5, 0, 0])
        player._callback(out, 4, None, None)
        np.testing.assert_array_equal(out, 0)

    def test_stereo_and_multiple_chunks(self):
        player = AudioPlayback(channels=2)
        player.play(np.ones((2, 2)))
        player.play(np.full((2, 2), 2))
        out = np.empty((4, 2))
        player._callback(out, 4, None, None)
        np.testing.assert_array_equal(out, [[1, 1], [1, 1], [2, 2], [2, 2]])

    def test_invalid_audio(self):
        player = AudioPlayback()
        for data in [np.zeros((4, 2)), np.array([np.nan]), np.array([np.inf])]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                player.play(data)

    def test_capture_drops_oldest_on_overflow(self):
        capture = AudioCapture()
        for i in range(101):
            capture._callback(np.array([i], dtype=np.float32).tobytes(), 1, None, None)
        self.assertEqual(capture._queue.qsize(), 100)
        self.assertEqual(capture.read()[0], 1)

    @patch('audio.capture.sd.RawInputStream')
    def test_capture_start_failure_closes_stream(self, stream_class):
        stream_class.return_value.start.side_effect = RuntimeError('device missing')
        capture = AudioCapture()
        with self.assertRaises(RuntimeError):
            capture.start()
        stream_class.return_value.close.assert_called_once()
        self.assertIsNone(capture._stream)
        self.assertFalse(capture._running)

    @patch('audio.playback.sd.OutputStream')
    def test_playback_uses_array_stream(self, stream_class):
        player = AudioPlayback()
        player.start()
        player.start()
        self.assertEqual(stream_class.call_count, 1)
        player.stop()
        stream_class.return_value.close.assert_called_once()


class LanguageTests(unittest.TestCase):
    def test_commands_and_normal_speech(self):
        manager = LanguageManager()
        for text, expected in [('switch to Tamil.', 'ta'), ('German!', 'de'),
                               ('speak French please', 'fr'), ('I speak French', None),
                               ('hello there', None)]:
            with self.subTest(text=text):
                self.assertEqual(manager.is_switch_command(text), expected)

    def test_switch_does_not_download_model(self):
        manager = LanguageManager()
        with patch.object(manager, '_load_model') as load:
            manager.switch_language('French')
            self.assertEqual(manager.current_lang, 'fr')
            load.assert_not_called()
            manager.switch_language('invalid')
            self.assertEqual(manager.current_lang, 'fr')

    def test_invalid_translation_target_fails_before_model_load(self):
        manager = LanguageManager()
        with patch.object(manager, '_load_model') as load:
            with self.assertRaises(ValueError):
                manager.translate('hello', 'invalid')
            load.assert_not_called()


class SpeechTests(unittest.TestCase):
    @patch.object(TTS, '_start_worker')
    @patch.object(TTS, '_check_edge_tts')
    def test_network_requires_explicit_opt_in(self, check, start):
        tts = TTS()
        check.assert_not_called()
        self.assertFalse(tts._edge_tts_available)
        TTS(allow_network=True)
        check.assert_called_once()

    @patch.object(TTS, '_start_worker')
    @patch('ai.tts.subprocess.run')
    def test_speech_passed_via_stdin(self, run, start):
        tts = TTS()
        tts._speak_sync('hello', 'fr')
        args = run.call_args.args[0]
        self.assertNotIn('hello', args)
        self.assertEqual(run.call_args.kwargs['input'], 'hello')
        self.assertNotIn('shell', run.call_args.kwargs)

    def test_speech_preserves_meaningful_punctuation(self):
        self.assertEqual(_sanitize_for_tts("  Don't pay -3.50!  "), "Don't pay -3.50!")

    def test_stop_rejects_new_speech(self):
        tts = TTS()
        tts.stop()
        with self.assertRaises(RuntimeError):
            tts.speak('hello')


class LifecycleTests(unittest.TestCase):
    def test_failed_capture_start_cleans_up_tts(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch('pipeline.orchestrator_v2.AudioCapture') as capture, \
             patch('pipeline.orchestrator_v2.VAD'), \
             patch('pipeline.orchestrator_v2.STT'), \
             patch('pipeline.orchestrator_v2.TTS') as tts:
            pipeline = Pipeline(latency_log=str(Path(tmp) / 'latency.csv'))
            capture.return_value.start.side_effect = RuntimeError('no microphone')
            with self.assertRaises(RuntimeError):
                pipeline.start()
            tts.return_value.stop.assert_called_once()
            self.assertFalse(pipeline._running)
            with self.assertRaises(RuntimeError):
                pipeline.start()

    def test_vad_does_not_process_audio_during_speech(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch('pipeline.orchestrator_v2.AudioCapture'), \
             patch('pipeline.orchestrator_v2.VAD'), \
             patch('pipeline.orchestrator_v2.STT'), \
             patch('pipeline.orchestrator_v2.TTS'):
            pipeline = Pipeline(latency_log=str(Path(tmp) / 'latency.csv'))
            pipeline.tts.busy = True
            pipeline._running = True

            def read(timeout):
                pipeline._running = False
                return np.ones(512, dtype=np.float32)

            pipeline.capture.read.side_effect = read
            pipeline._vad_worker()
            pipeline.vad.process.assert_not_called()
            pipeline.vad.reset.assert_called_once()

    def test_feedback_reset_is_deferred_to_vad_worker(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch('pipeline.orchestrator_v2.AudioCapture'), \
             patch('pipeline.orchestrator_v2.VAD'), \
             patch('pipeline.orchestrator_v2.STT'), \
             patch('pipeline.orchestrator_v2.TTS'):
            pipeline = Pipeline(latency_log=str(Path(tmp) / 'latency.csv'))
            pipeline._trans_queue.put('stale text')
            pipeline._clear_feedback()
            self.assertTrue(pipeline._reset_vad.is_set())
            self.assertTrue(pipeline._trans_queue.empty())
            pipeline.vad.reset.assert_not_called()

    def test_invalid_sample_rate_fails_before_initializing_models(self):
        with self.assertRaises(ValueError):
            Pipeline(sample_rate=44100)


if __name__ == '__main__':
    unittest.main()
