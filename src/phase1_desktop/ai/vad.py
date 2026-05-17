import torch
import numpy as np
from typing import Optional, Callable

"""
Silero VAD Wrapper — Phase 1

Detects speech in audio chunks. Uses a ring buffer to feed
exactly 512 samples per inference (Silero requirement at 16kHz).
"""


class VAD:
    def __init__(
        self,
        threshold: float = 0.5,
        min_speech_duration_ms: float = 250,
        sample_rate: int = 16000,
    ):
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.sample_rate = sample_rate
        self.model = None
        self._load_model()

        # State
        self.is_speaking = False
        self.speech_start = None
        self.speech_buffer = []
        self.ring_buffer = np.zeros(0, dtype=np.float32)

    def _load_model(self):
        self.model, _ = torch.hub.load(
            "snakers4/silero-vad",
            "silero_vad",
            trust_repo=True,
        )
        self.model.eval()

    def process(self, audio_chunk: np.ndarray) -> Optional[np.ndarray]:
        """
        Process audio chunk. Returns speech segment when speech ends,
        or None while speech is ongoing.
        """
        self.ring_buffer = np.concatenate((self.ring_buffer, audio_chunk))

        while len(self.ring_buffer) >= 512:
            chunk = self.ring_buffer[:512]
            self.ring_buffer = self.ring_buffer[512:]

            tensor = torch.from_numpy(chunk).unsqueeze(0)
            with torch.no_grad():
                prob = self.model(tensor, self.sample_rate).item()

            # State machine with hysteresis
            if not self.is_speaking and prob >= self.threshold:
                self.is_speaking = True
                self.speech_start = len(self.speech_buffer) * 512
                self.speech_buffer.append(chunk)

            elif self.is_speaking and prob < self.threshold - 0.15:
                duration_ms = len(self.speech_buffer) * 512 / self.sample_rate * 1000
                if duration_ms >= self.min_speech_duration_ms:
                    segment = np.concatenate(self.speech_buffer)
                    self.speech_buffer = []
                    self.is_speaking = False
                    self.speech_start = None
                    return segment
                else:
                    # Too short, discard
                    self.speech_buffer = []
                    self.is_speaking = False
                    self.speech_start = None

            elif self.is_speaking:
                self.speech_buffer.append(chunk)

        return None

    def reset(self):
        self.is_speaking = False
        self.speech_start = None
        self.speech_buffer = []
        self.ring_buffer = np.zeros(0, dtype=np.float32)
