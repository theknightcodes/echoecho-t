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
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def translate(self, text: str) -> str:
        """Translate text."""
        if not text.strip():
            return ""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True)
        outputs = self.model.generate(**inputs)
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
