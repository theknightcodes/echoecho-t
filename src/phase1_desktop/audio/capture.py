import sounddevice as sd
import numpy as np
import queue
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
            # Keep recent audio rather than accumulating stale conversation.
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(audio)
            except queue.Full:
                pass
        if self.on_audio:
            self.on_audio(audio)

    def start(self):
        if self._stream is not None:
            return
        self.drain()
        self._stream = sd.RawInputStream(
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

    def read(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def drain(self):
        """Remove all pending audio chunks from the queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
