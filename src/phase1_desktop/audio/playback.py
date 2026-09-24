import sounddevice as sd
import numpy as np
import queue
from typing import Optional

"""
Audio Playback Module — Phase 1

Plays audio chunks through speakers from a thread-safe queue.
"""


class AudioPlayback:
    def __init__(
        self,
        sample_rate: int = 16000,
        block_size: int = 512,
        channels: int = 1,
        dtype=np.float32,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.dtype = dtype
        self._queue = queue.Queue(maxsize=100)
        self._stream = None
        self._running = False
        self._pending = np.empty((0, channels), dtype=dtype)

    def _callback(self, outdata, frames, time_info, status):
        # OutputStream supplies a (frames, channels) ndarray. Preserve tails
        # across callbacks instead of discarding audio longer than one block.
        outdata.fill(0)
        offset = 0
        while offset < frames:
            if len(self._pending) == 0:
                try:
                    self._pending = self._queue.get_nowait()
                except queue.Empty:
                    break
            count = min(frames - offset, len(self._pending))
            outdata[offset:offset + count] = self._pending[:count]
            self._pending = self._pending[count:]
            offset += count

    def start(self):
        if self._stream is not None:
            return
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback,
        )
        try:
            self._stream.start()
            self._running = True
        except Exception:
            self._stream.close()
            self._stream = None
            raise

    def stop(self):
        self._running = False
        if self._stream:
            stream, self._stream = self._stream, None
            try:
                stream.stop()
            finally:
                stream.close()
        self._pending = np.empty((0, self.channels), dtype=self.dtype)
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def play(self, audio: np.ndarray):
        """Queue a copy; return False when backpressure rejects the audio."""
        audio = np.asarray(audio, dtype=self.dtype)
        if audio.ndim == 1 and self.channels == 1:
            audio = audio[:, None]
        if audio.ndim != 2 or audio.shape[1] != self.channels:
            raise ValueError("Audio shape must be (frames, channels)")
        if not np.isfinite(audio).all():
            raise ValueError("Audio must contain finite samples")
        if not len(audio):
            return True
        try:
            self._queue.put_nowait(audio.copy())
            return True
        except queue.Full:
            return False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
