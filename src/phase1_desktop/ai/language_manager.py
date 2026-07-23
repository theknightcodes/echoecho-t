from typing import Optional, Dict
import torch
import re

"""
Language Manager — Phase 1 (NLLB-200-distilled-600M Backend)

Uses a single multilingual model (facebook/nllb-200-distilled-600M)
for all translations. Supports 200 languages including Tamil, Japanese,
Korean, Polish.

NLLB-200 uses FLORES-200 language codes (e.g., tam_Taml, deu_Latn).
Model is loaded once in fp16 (~2.4GB RAM).
"""

# Model name
MODEL_NAME = "facebook/nllb-200-distilled-600M"

# EchoEcho language code → FLORES-200 language code
LANGUAGE_CODES = {
    "de": "deu_Latn",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
    "nl": "nld_Latn",
    "ru": "rus_Cyrl",
    "zh": "zho_Hans",
    "ja": "jpn_Jpan",
    "ko": "kor_Hang",
    "ta": "tam_Taml",
    "hi": "hin_Deva",
    "ar": "arb_Arab",
    "tr": "tur_Latn",
    "pl": "pol_Latn",
}

# Language code → display name
LANGUAGE_NAMES = {
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ta": "Tamil",
    "hi": "Hindi",
    "ar": "Arabic",
    "tr": "Turkish",
    "pl": "Polish",
}

# Greeting confirmations per language — NO punctuation so TTS doesn't read it aloud
LANGUAGE_GREETINGS = {
    "de": "Sprache auf Deutsch umgestellt",
    "fr": "Langue changée en français",
    "es": "Idioma cambiado a español",
    "it": "Lingua cambiata in italiano",
    "pt": "Idioma alterado para português",
    "nl": "Taal gewijzigd naar Nederlands",
    "ru": "Язык изменен на русский",
    "zh": "语言已切换为中文",
    "ja": "言語を日本語に変更しました",
    "ko": "언어가 한국어로 변경되었습니다",
    "ta": "மொழி தமிழுக்கு மாற்றப்பட்டது",
    "hi": "भाषा हिंदी में बदल दी गई है",
    "ar": "تم تغيير اللغة إلى العربية",
    "tr": "Dil Türkçe olarak değiştirildi",
    "pl": "Język zmieniony na polski",
}


class LanguageManager:
    def __init__(self, default_lang: str = "de"):
        if default_lang not in LANGUAGE_CODES:
            raise ValueError(
                f"Invalid default language: {default_lang}. "
                f"Supported: {list(LANGUAGE_CODES.keys())}"
            )
        self.current_lang = default_lang
        self._model = None
        self._tokenizer = None
        self._device = None

    def _load_model(self):
        """Lazy-load NLLB-200-distilled-600M once."""
        if self._model is not None:
            return

        print("[LanguageManager] Loading NLLB-200-distilled-600M (one-time ~2.4GB)...")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            self._device = self._model.device
            print(f"[LanguageManager] Model loaded on {self._device}")
        except Exception:
            raise RuntimeError(
                "Failed to load NLLB-200-distilled-600M. "
                "Ensure ~3GB free RAM and stable internet."
            )

    def translate(self, text: str, target_lang: Optional[str] = None) -> str:
        """Translate English text to target language using NLLB-200."""
        lang = target_lang or self.current_lang
        text = text.strip()
        if not text:
            return ""

        # Validate input length (prevent abuse / excessive compute)
        if len(text) > 500:
            text = text[:500]

        self._load_model()

        flores_code = LANGUAGE_CODES.get(lang)
        if not flores_code:
            raise ValueError(f"Unsupported language: {lang}")

        self._tokenizer.src_lang = "eng_Latn"
        inputs = self._tokenizer(text, return_tensors="pt").to(self._device)
        forced_bos = self._tokenizer.convert_tokens_to_ids(flores_code)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                forced_bos_token_id=forced_bos,
                max_new_tokens=128,
            )

        result = self._tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return result

    def switch_language(self, lang_code: str) -> str:
        """Switch to a new language. Returns confirmation message."""
        lang_code = lang_code.lower().strip()

        # Handle full names
        name_to_code = {v.lower(): k for k, v in LANGUAGE_NAMES.items()}
        if lang_code in name_to_code:
            lang_code = name_to_code[lang_code]

        if lang_code not in LANGUAGE_CODES:
            supported = ", ".join([f"{k} ({v})" for k, v in LANGUAGE_NAMES.items()])
            return f"Unsupported language '{lang_code}'. Supported: {supported}"

        self.current_lang = lang_code

        # Warm up model on first switch
        try:
            self._load_model()
        except RuntimeError as e:
            return str(e)

        greeting = LANGUAGE_GREETINGS.get(
            lang_code, f"Language switched to {LANGUAGE_NAMES.get(lang_code, lang_code)}"
        )
        return greeting

    def get_current_language(self) -> str:
        return LANGUAGE_NAMES.get(self.current_lang, self.current_lang)

    def is_switch_command(self, text: str) -> Optional[str]:
        """Detect if text is a language switch command."""
        text_lower = text.lower().strip()

        switch_patterns = [
            "switch to ", "change to ", "switch language to ",
            "speak ", "use ", "translate to ", "set language to ",
            "language ", "lang ",
            "tamil", "hindi", "japanese", "chinese", "german", "french",
            "spanish", "korean", "arabic", "russian", "italian",
            "portuguese", "dutch", "turkish", "polish",
        ]

        for pattern in switch_patterns:
            has_space = " " in pattern
            if has_space and text_lower.startswith(pattern):
                lang_part = text_lower[len(pattern):].strip()
            elif not has_space and text_lower == pattern.strip():
                lang_part = pattern.strip()
            else:
                continue

            name_to_code = {v.lower(): k for k, v in LANGUAGE_NAMES.items()}
            if lang_part in name_to_code:
                return name_to_code[lang_part]
            if lang_part in LANGUAGE_CODES:
                return lang_part

            # Allow trailing words, e.g. "switch to Tamil please"
            first_word = lang_part.split(" ", 1)[0] if lang_part else ""
            if first_word in name_to_code:
                return name_to_code[first_word]
            if first_word in LANGUAGE_CODES:
                return first_word

        return None
