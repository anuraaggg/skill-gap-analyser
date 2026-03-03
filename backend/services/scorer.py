from typing import Dict, List, Optional


DEFAULT_CATEGORY_WEIGHTS = {
    "core": 5,
    "supporting": 3,
    "optional": 1,
}


class WeightedReadinessScorer:
    def __init__(self, category_weights: Optional[Dict[str, int]] = None):
        self.category_weights = {**DEFAULT_CATEGORY_WEIGHTS, **(category_weights or {})}

    def categorize_job_skills(
        self,
        job_skills: List[str],
        category_overrides: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        overrides = {k.lower(): v.lower() for k, v in (category_overrides or {}).items()}
        categorized: List[Dict] = []
        for skill in job_skills:
            category = overrides.get(skill.lower(), "core")
            if category not in self.category_weights:
                category = "core"
            categorized.append(
                {
                    "skill": skill,
                    "category": category,
                    "weight": self.category_weights[category],
                }
            )
        return categorized

    def compute_readiness_score(self, matches: List[Dict], categorized_skills: List[Dict]) -> Dict:
        by_skill = {item["skill"]: item for item in categorized_skills}
        total_weight = sum(item["weight"] for item in categorized_skills)
        weighted_score_sum = 0.0

        contributions: List[Dict] = []
        matched_skills: List[Dict] = []
        missing_skills: List[Dict] = []
        explanations: List[str] = []
        explanation_json: List[Dict] = []
        for match in matches:
            category_record = by_skill.get(match["job_skill"], {"category": "core", "weight": self.category_weights["core"]})
            skill_weight = category_record["weight"]
            skill_category = category_record["category"]
            # Weighted reasoning rule:
            # - If a skill is matched, contribution = weight * similarity_score.
            # - If a skill is not matched, contribution = 0.
            similarity_score = float(match["similarity_score"]) if match["is_matched"] else 0.0
            contribution = skill_weight * similarity_score
            weighted_score_sum += contribution
            contribution_record = {
                "skill": match["job_skill"],
                "category": skill_category,
                "weight": skill_weight,
                "matched_resume_skill": match["matched_resume_skill"],
                "similarity_score": round(similarity_score, 4),
                "contribution": round(contribution, 4),
            }
            contributions.append(contribution_record)

            if match["is_matched"]:
                matched_skills.append(contribution_record)
                explanation_text = (
                    f"Matched {skill_category.title()} Skill '{match['job_skill']}' with resume skill "
                    f"'{match['matched_resume_skill']}' (similarity={round(similarity_score, 2):.2f}). "
                    f"Contribution: {round(contribution, 2):.2f}/{skill_weight}."
                )
                explanations.append(explanation_text)
                explanation_json.append(
                    {
                        "skill": match["job_skill"],
                        "category": skill_category,
                        "weight": skill_weight,
                        "status": "matched",
                        "matched_resume_skill": match["matched_resume_skill"],
                        "similarity_score": round(similarity_score, 4),
                        "contribution": round(contribution, 4),
                        "max_contribution": float(skill_weight),
                        "message": explanation_text,
                    }
                )
            else:
                missing_skills.append(
                    {
                        "skill": match["job_skill"],
                        "category": skill_category,
                        "weight": skill_weight,
                    }
                )
                explanation_text = (
                    f"Missing {skill_category.title()} Skill '{match['job_skill']}'. "
                    f"This reduces the readiness score by potential {skill_weight} points."
                )
                explanations.append(explanation_text)
                explanation_json.append(
                    {
                        "skill": match["job_skill"],
                        "category": skill_category,
                        "weight": skill_weight,
                        "status": "missing",
                        "matched_resume_skill": None,
                        "similarity_score": 0.0,
                        "contribution": 0.0,
                        "max_contribution": float(skill_weight),
                        "message": explanation_text,
                    }
                )

        # Final weighted readiness score:
        # readiness_score = (sum(contributions) / total_weight) * 100
        readiness_score = (weighted_score_sum / total_weight * 100) if total_weight else 0.0
        return {
            "readiness_score": round(readiness_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "explanations": explanations,
            "explanations_json": explanation_json,
            "total_weight": total_weight,
            "weighted_score_sum": round(weighted_score_sum, 4),
            "contributions": contributions,
        }
