import re
from typing import List, Optional

from spacy.lang.en import English


class SkillExtractor:
    def __init__(self, skills_patterns_path: Optional[str] = None):
        self.skills_patterns_path = skills_patterns_path
        self._nlp = English()
        self._ruler = self._nlp.add_pipe("entity_ruler")
        if skills_patterns_path:
            self._ruler.from_disk(skills_patterns_path)

    @staticmethod
    def _clean(skill: str) -> str:
        return re.sub(r"\s+", " ", skill).strip()

    def extract_from_text(self, text: str) -> List[str]:
        if not text:
            return []

        doc = self._nlp(text)
        extracted_skills: List[str] = []
        for ent in doc.ents:
            label_parts = ent.label_.split("|")
            if label_parts and label_parts[0] == "SKILL":
                normalized = label_parts[1].replace("-", " ") if len(label_parts) > 1 else ent.text
                normalized = self._clean(normalized)
                if normalized and normalized not in extracted_skills:
                    extracted_skills.append(normalized)
        return extracted_skills

    def extract_from_list(self, skills: List[str]) -> List[str]:
        if not skills:
            return []
        unique_skills: List[str] = []
        for skill in skills:
            cleaned = self._clean(str(skill))
            if cleaned and cleaned not in unique_skills:
                unique_skills.append(cleaned)
        return unique_skills
