import numpy as np
from typing import Optional

"""
Speech-to-Text Wrapper — Phase 1

Wraps faster-whisper for transcription.
"""


class STT:
    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = "en",
        beam_size: int = 5,
    ):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.language = language  # Force English for source speech
        self.beam_size = beam_size

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        """
        Transcribe audio segment.
        Returns: (transcript, detected_language)
        """
        segments, info = self.model.transcribe(
            audio,
            beam_size=self.beam_size,
            language=self.language,
            condition_on_previous_text=False,
        )
        text = " ".join([s.text.strip() for s in segments])
        return text, info.language
