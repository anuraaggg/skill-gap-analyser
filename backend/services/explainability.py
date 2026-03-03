from typing import Dict, List


class ExplainabilityReportBuilder:
    @staticmethod
    def _missing_impact(weight: int, total_weight: int) -> float:
        if total_weight == 0:
            return 0.0
        return round((weight / total_weight) * 100, 2)

    def build_report(self, scoring_output: Dict, similarity_threshold: float) -> Dict:
        contributions = scoring_output.get("contributions", [])
        total_weight = scoring_output.get("total_weight", 0)
        intrinsic_explanations = scoring_output.get("explanations", [])
        intrinsic_explanations_json = scoring_output.get("explanations_json", [])
        readiness_score = scoring_output.get("readiness_score", 0.0)

        missing_core_skills: List[str] = []
        missing_supporting_skills: List[str] = []
        strong_matched_skills: List[str] = []
        detailed_lines: List[Dict] = []
        recommendations: List[str] = []
        core_skill_recommendations: List[str] = []
        supporting_skill_recommendations: List[str] = []

        for item in contributions:
            is_missing = item.get("matched_resume_skill") is None
            similarity_score = item.get("similarity_score", 0.0)
            category = item.get("category")
            job_skill = item.get("skill")
            weight = item.get("weight", 0)

            if is_missing:
                impact = self._missing_impact(weight, total_weight)
                if category == "core":
                    missing_core_skills.append(job_skill)
                elif category == "supporting":
                    missing_supporting_skills.append(job_skill)
                detailed_lines.append(
                    {
                        **item,
                        "impact_explanation": f"Missing skill reduces potential score by approximately {impact}%.",
                    }
                )
            else:
                if similarity_score >= max(similarity_threshold, 0.85):
                    strong_matched_skills.append(job_skill)
                detailed_lines.append(
                    {
                        **item,
                        "impact_explanation": "Skill contributes positively to readiness based on weighted similarity.",
                    }
                )

        for skill in missing_core_skills:
            core_skill_recommendations.append(
                f"Consider gaining experience in {skill} to improve readiness."
            )

        for skill in missing_supporting_skills:
            supporting_skill_recommendations.append(
                f"Consider strengthening {skill} as an optional enhancement to improve profile depth."
            )

        if core_skill_recommendations:
            recommendations.extend(core_skill_recommendations)
        if supporting_skill_recommendations:
            recommendations.extend(supporting_skill_recommendations)
        if strong_matched_skills:
            recommendations.append(
                "Strength areas to emphasize: " + ", ".join(strong_matched_skills)
            )
        if not recommendations:
            recommendations.append(
                "Skill alignment is strong; maintain current strengths and tailor examples to job context."
            )

        if missing_core_skills and readiness_score < 50:
            overall_assessment = "Low readiness due to multiple core skill gaps."
        elif missing_core_skills:
            overall_assessment = "Moderate readiness with critical core skill gaps to close."
        elif readiness_score >= 80:
            overall_assessment = "High readiness with strong alignment to job skills."
        elif readiness_score >= 60:
            overall_assessment = "Good baseline readiness with room for targeted improvement."
        else:
            overall_assessment = "Early-stage readiness; improve supporting and optional skills."

        final_summary = {
            "strength_areas": strong_matched_skills,
            "major_skill_gaps": missing_core_skills,
            "overall_candidate_assessment": overall_assessment,
        }

        return {
            "readiness_score": readiness_score,
            "formula": "ReadinessScore = (Sum of MatchedSkillWeight × SimilarityScore) / TotalWeight × 100",
            "intrinsic_explanations": intrinsic_explanations,
            "intrinsic_explanations_json": intrinsic_explanations_json,
            "detailed_skill_analysis": detailed_lines,
            "skill_gap_report": {
                "missing_core_skills": missing_core_skills,
                "missing_supporting_skills": missing_supporting_skills,
                "strong_matched_skills": strong_matched_skills,
            },
            "recommendation_generator": {
                "core_skill_recommendations": core_skill_recommendations,
                "supporting_skill_recommendations": supporting_skill_recommendations,
            },
            "recommendations": recommendations,
            "final_summary": final_summary,
        }
