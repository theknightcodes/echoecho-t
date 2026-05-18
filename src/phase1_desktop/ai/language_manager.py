from typing import Optional, Dict
import os

"""
Language Manager — Phase 1

Manages multiple translation models and switches between them.
Models are loaded lazily (on first use) to save memory.
"""

# Language code → model mapping
# Only includes models verified to exist on HuggingFace
LANGUAGE_MODELS = {
    "de": "Helsinki-NLP/opus-mt-en-de",
    "fr": "Helsinki-NLP/opus-mt-en-fr",
    "es": "Helsinki-NLP/opus-mt-en-es",
    "it": "Helsinki-NLP/opus-mt-en-it",
    "pt": "Helsinki-NLP/opus-mt-tc-big-en-pt",  # tc-big model available
    "nl": "Helsinki-NLP/opus-mt-en-nl",
    "ru": "Helsinki-NLP/opus-mt-en-ru",
    "zh": "Helsinki-NLP/opus-mt-en-zh",
    # "ja": "Helsinki-NLP/opus-mt-en-jap",  # LOADS but produces gibberish — use NLLB-200 in Phase 2
    # "ko": "Helsinki-NLP/opus-mt-tc-big-en-ko",  # LOADS but produces toxic/gibberish output — use NLLB-200 in Phase 2
    # "ta": "Helsinki-NLP/opus-mt-en-ta",  # Not available — use NLLB-200 for Tamil
    "hi": "Helsinki-NLP/opus-mt-en-hi",
    "ar": "Helsinki-NLP/opus-mt-en-ar",
    "tr": "Helsinki-NLP/opus-mt-tc-big-en-tr",  # tc-big model available
    # "pl": "Helsinki-NLP/opus-mt-en-pl",  # No English-to-Polish model exists in Helsinki-NLP
}

LANGUAGE_NAMES = {
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
    # "ja": "Japanese",  # No quality model available in Helsinki-NLP
    # "ko": "Korean",    # No quality model available in Helsinki-NLP
    # "ta": "Tamil",  # Not available in Helsinki-NLP, use NLLB-200
    "hi": "Hindi",
    "ar": "Arabic",
    "tr": "Turkish",
    # "pl": "Polish",  # No English-to-Polish model exists in Helsinki-NLP
}

# Greeting confirmations per language
LANGUAGE_GREETINGS = {
    "de": "Sprache auf Deutsch umgestellt.",
    "fr": "Langue changée en français.",
    "es": "Idioma cambiado a español.",
    "it": "Lingua cambiata in italiano.",
    "pt": "Idioma alterado para português.",
    "nl": "Taal gewijzigd naar Nederlands.",
    "ru": "Язык изменен на русский.",
    "zh": "语言已切换为中文。",
    # "ja": "言語を日本語に変更しました。",  # No quality model available in Helsinki-NLP
    # "ko": "언어가 한국어로 변경되었습니다。",  # No quality model available in Helsinki-NLP
    # "ta": "மொழி தமிழுக்கு மாற்றப்பட்டது.",  # Not available
    "hi": "भाषा हिंदी में बदल दी गई है।",
    "ar": "تم تغيير اللغة إلى العربية.",
    "tr": "Dil Türkçe olarak değiştirildi.",
    # "pl": "Język zmieniony na polski.",  # No model available
}


class LanguageManager:
    def __init__(self, default_lang: str = "de"):
        self.current_lang = default_lang
        self._models: Dict[str, any] = {}
        self._tokenizers: Dict[str, any] = {}

    def _load_model(self, lang_code: str):
        """Lazy-load model for language."""
        if lang_code in self._models:
            return self._models[lang_code], self._tokenizers[lang_code]

        model_name = LANGUAGE_MODELS.get(lang_code)
        if not model_name:
            raise ValueError(f"Unsupported language: {lang_code}. Supported: {list(LANGUAGE_MODELS.keys())}")

        print(f"[LanguageManager] Loading model for {LANGUAGE_NAMES.get(lang_code, lang_code)}...")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        except Exception as e:
            print(f"[LanguageManager] ERROR loading {model_name}: {e}")
            raise RuntimeError(
                f"Failed to load model for {LANGUAGE_NAMES.get(lang_code, lang_code)}. "
                f"Model may not exist or requires authentication. Error: {e}"
            )

        self._models[lang_code] = model
        self._tokenizers[lang_code] = tokenizer
        print(f"[LanguageManager] {LANGUAGE_NAMES.get(lang_code, lang_code)} model ready.")
        return model, tokenizer

    def translate(self, text: str, target_lang: Optional[str] = None) -> str:
        """Translate text to target language (or current language)."""
        lang = target_lang or self.current_lang
        if not text.strip():
            return ""

        model, tokenizer = self._load_model(lang)
        inputs = tokenizer(text, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result

    def switch_language(self, lang_code: str) -> str:
        """Switch to a new language. Returns confirmation message."""
        lang_code = lang_code.lower().strip()

        # Handle full names
        name_to_code = {v.lower(): k for k, v in LANGUAGE_NAMES.items()}
        if lang_code in name_to_code:
            lang_code = name_to_code[lang_code]

        if lang_code not in LANGUAGE_MODELS:
            supported = ", ".join([f"{k} ({v})" for k, v in LANGUAGE_NAMES.items()])
            return f"Unsupported language '{lang_code}'. Supported: {supported}"

        self.current_lang = lang_code

        # Load model immediately so it's ready
        try:
            self._load_model(lang_code)
        except RuntimeError as e:
            return str(e)

        # Return greeting in target language
        greeting = LANGUAGE_GREETINGS.get(lang_code, f"Language switched to {LANGUAGE_NAMES.get(lang_code, lang_code)}.")
        return greeting

    def get_current_language(self) -> str:
        return LANGUAGE_NAMES.get(self.current_lang, self.current_lang)

    def is_switch_command(self, text: str) -> Optional[str]:
        """
        Detect if text is a language switch command.
        Returns target language code or None.
        """
        text_lower = text.lower().strip()

        # Pattern: "switch to X", "change to X", "speak X", "use X"
        switch_patterns = [
            "switch to ", "change to ", "switch language to ",
            "speak ", "use ", "translate to ", "set language to ",
            "language ", "lang ", "tamil", "hindi",  # "japanese", "korean" — no models available
            "chinese", "german", "french", "spanish",  # "korean" — no model available
            "arabic", "russian", "italian", "portuguese", "dutch",
            "turkish",  # "polish", "japanese", "korean" — no models available
        ]

        for pattern in switch_patterns:
            if text_lower.startswith(pattern) or text_lower == pattern.strip():
                # Extract language from command
                if " " in pattern:
                    lang_part = text_lower[len(pattern):].strip()
                else:
                    lang_part = pattern.strip()

                # Map to code
                name_to_code = {v.lower(): k for k, v in LANGUAGE_NAMES.items()}
                if lang_part in name_to_code:
                    return name_to_code[lang_part]
                if lang_part in LANGUAGE_MODELS:
                    return lang_part

        return None
