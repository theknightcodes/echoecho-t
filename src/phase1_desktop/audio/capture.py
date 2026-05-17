import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Callable, Optional

"""
Audio Capture Module — Phase 1

Streams audio from microphone into a thread-safe queue.
Works with the pipeline orchestrator.
"""


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = 16000,
        block_size: int = 512,
        channels: int = 1,
        dtype=np.float32,
        on_audio: Optional[Callable[[np.ndarray], None]] = None,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.dtype = dtype
        self.on_audio = on_audio
        self._queue = queue.Queue(maxsize=100)
        self._stream = None
        self._running = False
        self._thread = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[AudioCapture] {status}")
        # Convert CFFI buffer to numpy
        audio = np.frombuffer(indata, dtype=self.dtype).copy()
        try:
            self._queue.put_nowait(audio)
        except queue.Full:
            pass  # Drop oldest if full
        if self.on_audio:
            self.on_audio(audio)

    def start(self):
        self._running = True
        self._stream = sd.RawInputStream(
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

    def read(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
