from typing import Dict, List

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSkillMatcher:
    def __init__(self, model_name: str = "all-mpnet-base-v2", threshold: float = 0.7):
        self.model_name = model_name
        self.threshold = threshold
        self.model = SentenceTransformer(model_name)

    def match(self, job_skills: List[str], resume_skills: List[str]) -> List[Dict]:
        if not job_skills:
            return []

        if not resume_skills:
            return [
                {
                    "job_skill": job_skill,
                    "matched_resume_skill": None,
                    "similarity_score": 0.0,
                    "is_matched": False,
                }
                for job_skill in job_skills
            ]

        job_embeddings = self.model.encode(job_skills)
        resume_embeddings = self.model.encode(resume_skills)

        results: List[Dict] = []
        for index, job_skill in enumerate(job_skills):
            similarities = cosine_similarity([job_embeddings[index]], resume_embeddings)[0]
            best_idx = int(similarities.argmax())
            best_score = float(similarities[best_idx])
            matched_skill = resume_skills[best_idx]
            results.append(
                {
                    "job_skill": job_skill,
                    "matched_resume_skill": matched_skill if best_score >= self.threshold else None,
                    "similarity_score": round(best_score, 4),
                    "is_matched": best_score >= self.threshold,
                }
            )
        return results
