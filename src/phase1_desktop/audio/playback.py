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
        self._silence = np.zeros(block_size, dtype=dtype)

    def _callback(self, outdata, frames, time_info, status):
        if status:
            print(f"[AudioPlayback] {status}")
        try:
            chunk = self._queue.get_nowait()
            if len(chunk) < len(outdata):
                outdata[:len(chunk), 0] = chunk
                outdata[len(chunk):, 0] = 0
            else:
                outdata[:, 0] = chunk[:len(outdata)]
        except queue.Empty:
            outdata[:, 0] = self._silence[:len(outdata)]

    def start(self):
        self._running = True
        self._stream = sd.RawOutputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def play(self, audio: np.ndarray):
        """Queue audio for playback."""
        try:
            self._queue.put_nowait(audio)
        except queue.Full:
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
