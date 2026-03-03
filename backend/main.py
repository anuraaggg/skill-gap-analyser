from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from pathlib import Path
from io import BytesIO
from docx import Document
from pypdf import PdfReader
from services.skill_extractor import SkillExtractor
from services.normalizer import SkillNormalizer
from services.matcher import SemanticSkillMatcher
from services.scorer import WeightedReadinessScorer
from services.explainability import ExplainabilityReportBuilder


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SkillGapAnalysisRequest(BaseModel):
    resume_text: Optional[str] = None
    job_text: Optional[str] = None
    resume_skills: List[str] = Field(default_factory=list)
    job_skills: List[str] = Field(default_factory=list)
    skill_variations: Dict[str, str] = Field(default_factory=dict)
    category_weights: Dict[str, int] = Field(default_factory=dict)
    job_skill_categories: Dict[str, str] = Field(default_factory=dict)
    similarity_threshold: float = 0.7
    model_name: str = "all-mpnet-base-v2"


def _extract_text_from_resume_file(filename: str, content: bytes) -> str:
    lower_name = filename.lower()
    if lower_name.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    if lower_name.endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)

    if lower_name.endswith(".docx"):
        document = Document(BytesIO(content))
        paragraph_text = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraph_text)

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Please upload a .pdf, .docx, or .txt resume.",
    )


def _run_skill_gap_analysis(request: SkillGapAnalysisRequest) -> Dict:
    skills_patterns_path = str(BASE_DIR / "Resources" / "data" / "skills.jsonl")

    extractor = SkillExtractor(skills_patterns_path=skills_patterns_path)
    normalizer = SkillNormalizer(custom_variations=request.skill_variations)
    matcher = SemanticSkillMatcher(model_name=request.model_name, threshold=request.similarity_threshold)
    scorer = WeightedReadinessScorer(category_weights=request.category_weights)
    explainability = ExplainabilityReportBuilder()

    raw_job_skills = request.job_skills or extractor.extract_from_text(request.job_text or "")
    raw_resume_skills = request.resume_skills or extractor.extract_from_text(request.resume_text or "")

    normalized_job_skills = normalizer.normalize_skills(extractor.extract_from_list(raw_job_skills))
    normalized_resume_skills = normalizer.normalize_skills(extractor.extract_from_list(raw_resume_skills))

    categorized_job_skills = scorer.categorize_job_skills(
        normalized_job_skills,
        category_overrides=request.job_skill_categories,
    )
    skill_matches = matcher.match(normalized_job_skills, normalized_resume_skills)
    scoring_output = scorer.compute_readiness_score(skill_matches, categorized_job_skills)
    explanation_report = explainability.build_report(scoring_output, request.similarity_threshold)

    return {
        "inputs": {
            "job_skills_raw": raw_job_skills,
            "resume_skills_raw": raw_resume_skills,
            "job_skills_normalized": normalized_job_skills,
            "resume_skills_normalized": normalized_resume_skills,
            "similarity_threshold": request.similarity_threshold,
            "category_weights": scorer.category_weights,
        },
        "categorized_job_skills": categorized_job_skills,
        "matches": skill_matches,
        "score": {
            "readiness_score": scoring_output["readiness_score"],
            "matched_skills": scoring_output["matched_skills"],
            "missing_skills": scoring_output["missing_skills"],
            "explanations": scoring_output["explanations"],
            "explanations_json": scoring_output["explanations_json"],
            "total_weight": scoring_output["total_weight"],
            "weighted_score_sum": scoring_output["weighted_score_sum"],
        },
        "explanation": explanation_report,
    }

@app.get("/")
async def root():
    return {"message": "AI Resume Skill Gap Analyzer API is running."}


@app.post("/skill_gap_analyzer")
async def skill_gap_analyzer(request: SkillGapAnalysisRequest):
    return _run_skill_gap_analysis(request)


@app.post("/skill_gap_analyzer/upload")
async def skill_gap_analyzer_upload(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    similarity_threshold: float = Form(0.7),
    model_name: str = Form("all-mpnet-base-v2"),
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    file_bytes = await resume_file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded resume file is empty.")

    resume_text = _extract_text_from_resume_file(resume_file.filename or "resume.txt", file_bytes)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from resume file.")

    analysis_request = SkillGapAnalysisRequest(
        resume_text=resume_text,
        job_text=job_description,
        similarity_threshold=similarity_threshold,
        model_name=model_name,
    )
    response = _run_skill_gap_analysis(analysis_request)
    response["extracted_text"] = {
        "resume_filename": resume_file.filename,
        "resume_text_preview": resume_text[:1000],
        "job_description_preview": job_description[:1000],
    }
    return response
