import re
from typing import Dict, List, Optional

from spacy.lang.en import English


DEFAULT_VARIATIONS = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "nlp": "natural language processing",
    "ai": "artificial intelligence",
    "pytorch experience": "pytorch",
}


class SkillNormalizer:
    def __init__(self, custom_variations: Optional[Dict[str, str]] = None):
        self.variations = {**DEFAULT_VARIATIONS, **(custom_variations or {})}
        self._nlp = English()
        self._lemmatizer_enabled = False
        try:
            self._nlp.add_pipe("lemmatizer", config={"mode": "rule"})
            self._nlp.initialize()
            self._lemmatizer_enabled = True
        except Exception:
            self._lemmatizer_enabled = False

    @staticmethod
    def _basic_clean(skill: str) -> str:
        text = skill.lower().strip()
        text = re.sub(r"\b(experience|proficiency|knowledge|skills?)\b", "", text)
        text = re.sub(r"[^a-z0-9\+\.#\-/\s]", " ", text)
        text = text.replace("-", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _lemmatize(self, text: str) -> str:
        if not text:
            return ""
        if not self._lemmatizer_enabled:
            return text

        try:
            doc = self._nlp(text)
            lemmas = [token.lemma_ if token.lemma_ != "-PRON-" else token.text for token in doc]
            return " ".join(lemmas)
        except Exception:
            self._lemmatizer_enabled = False
            return text

    def normalize_skill(self, skill: str) -> str:
        base = self._basic_clean(skill)
        if not base:
            return ""

        base = self.variations.get(base, base)
        base = self._lemmatize(base)
        base = re.sub(r"\s+", " ", base).strip()
        return self.variations.get(base, base)

    def normalize_skills(self, skills: List[str]) -> List[str]:
        normalized: List[str] = []
        for skill in skills:
            result = self.normalize_skill(str(skill))
            if result and result not in normalized:
                normalized.append(result)
        return normalized
