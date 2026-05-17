from typing import Optional

"""
Translation Wrapper — Phase 1

Uses Helsinki-NLP opus-mt models (lightweight alternative to NLLB).
"""


class Translator:
    def __init__(
        self,
        model_name: str = "Helsinki-NLP/opus-mt-en-de",
        source_lang: str = "en",
        target_lang: str = "de",
    ):
        from transformers import pipeline

        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model_name = model_name
        self.pipeline = pipeline("text2text-generation", model=model_name)

    def translate(self, text: str) -> str:
        """Translate text."""
        if not text.strip():
            return ""
        result = self.pipeline(text, max_length=100)
        return result[0]["generated_text"]
