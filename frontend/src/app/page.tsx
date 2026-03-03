"use client";

import { FormEvent, useMemo, useState } from "react";
import Aurora from "@/components/Aurora";

type AnalyzerResponse = {
  inputs?: {
    job_skills_normalized?: string[];
    resume_skills_normalized?: string[];
  };
  score?: {
    readiness_score?: number;
    explanations?: string[];
    matched_skills?: Array<{ skill: string; contribution: number }>;
    missing_skills?: Array<{ skill: string; weight: number }>;
  };
  explanation?: {
    final_summary?: {
      strength_areas?: string[];
      major_skill_gaps?: string[];
      overall_candidate_assessment?: string;
    };
  };
};

export default function Home() {
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState("0.7");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzerResponse | null>(null);

  const apiBaseUrl = useMemo(() => {
    return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  }, []);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!resumeFile) {
      setError("Please upload a resume file (.pdf, .docx, or .txt).");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please paste the job description.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("job_description", jobDescription);
      formData.append("similarity_threshold", threshold);

      const response = await fetch(`${apiBaseUrl}/skill_gap_analyzer/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: AnalyzerResponse = await response.json();
      setResult(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to call analyzer API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950 px-6 py-10 text-white">
      <Aurora colorStops={["#5227FF", "#7cff67", "#5227FF"]} amplitude={0.55} blend={0.3} speed={0.7} />
      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-5xl flex-col items-center justify-center gap-7 text-center">
        <h1 className="font-display bg-linear-to-r from-white via-violet-200 to-emerald-200 bg-clip-text px-6 py-3 text-4xl font-semibold tracking-tight text-transparent [text-shadow:0_2px_16px_rgba(0,0,0,0.45)] motion-safe:animate-[pulse_4s_ease-in-out_infinite]">
          AI Resume Skill Gap Analyzer
        </h1>
        <p className="max-w-2xl text-sm leading-relaxed text-white/85 md:text-base">
          Upload a resume, paste the job description, and get a clear readiness score with matched skills, missing skills, and deterministic explanations.
        </p>

        <form
          onSubmit={onSubmit}
          className="w-full rounded-2xl border border-white/35 bg-black/35 p-6 shadow-[0_8px_30px_rgba(0,0,0,0.35)] backdrop-blur-md transition-all duration-300 hover:border-white/55 hover:bg-black/40"
        >
          <div className="grid gap-4 md:grid-cols-2 text-left">
            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold tracking-wide text-white/95">Job description</span>
              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                rows={8}
                className="w-full rounded-xl border border-white/45 bg-black/30 p-3 text-white outline-none transition-colors duration-200 placeholder:text-white/60 focus:border-white/80"
                placeholder="Paste the full job description here"
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold tracking-wide text-white/95">Resume file (.pdf, .docx, .txt)</span>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
                className="w-full rounded-xl border border-white/45 bg-black/30 p-3 text-white transition-colors duration-200 file:mr-3 file:rounded-lg file:border-0 file:bg-white file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-black hover:border-white/70"
              />
              <p className="text-xs text-white/80">{resumeFile ? `Selected: ${resumeFile.name}` : "No file selected"}</p>
              <div className="rounded-xl border border-white/20 bg-black/20 p-3 text-xs text-white/80 transition-colors duration-200 hover:border-white/40 hover:text-white/95">
                Tip: paste a complete JD with tools, frameworks, and responsibilities for better skill extraction.
              </div>
            </label>
          </div>

          <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
            <label className="text-sm font-semibold tracking-wide text-white/95" htmlFor="threshold">
              Similarity threshold
            </label>
            <input
              id="threshold"
              value={threshold}
              onChange={(event) => setThreshold(event.target.value)}
              className="w-24 rounded-xl border border-white/45 bg-black/30 p-2 text-center text-white outline-none transition-colors duration-200 focus:border-white/80"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl border border-white/80 bg-white px-5 py-2 text-sm font-semibold text-black transition-all duration-200 hover:scale-[1.03] hover:bg-white/90 active:scale-100 disabled:opacity-60"
            >
              {loading ? "Analyzing Resume..." : "Analyze"}
            </button>
          </div>
        </form>

        {error ? <p className="w-full rounded-md bg-red-500/30 p-3 text-red-100">{error}</p> : null}

        {result ? (
          <section className="w-full rounded-2xl border border-white/35 bg-black/35 p-6 shadow-[0_8px_30px_rgba(0,0,0,0.35)] backdrop-blur-md transition-all duration-300 hover:border-white/55 hover:bg-black/40">
            <h2 className="font-display bg-linear-to-r from-white via-violet-200 to-emerald-200 bg-clip-text text-xl font-semibold tracking-tight text-transparent">
              Analysis Result
            </h2>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-4">
              <div className="rounded-xl border border-white/30 bg-black/30 px-5 py-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-white/60 hover:bg-black/40">
                <p className="text-xs uppercase tracking-wide text-white/70">Readiness Score</p>
                <p className="font-display bg-linear-to-r from-white to-emerald-200 bg-clip-text text-3xl font-semibold text-transparent">
                  {result.score?.readiness_score ?? 0}%
                </p>
              </div>
              <div className="rounded-xl border border-white/30 bg-black/30 px-5 py-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-white/60 hover:bg-black/40">
                <p className="text-xs uppercase tracking-wide text-white/70">Overall Assessment</p>
                <p className="text-sm text-white/95">{result.explanation?.final_summary?.overall_candidate_assessment || "N/A"}</p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="font-display font-medium">Missing Skills</h3>
                {(result.score?.missing_skills || []).length === 0 ? (
                  <p className="mt-2 text-sm text-emerald-300">No missing skills detected.</p>
                ) : (
                  <ul className="mt-2 flex flex-wrap justify-center gap-2 text-sm text-white/95 md:justify-start">
                    {(result.score?.missing_skills || []).map((item) => (
                      <li key={item.skill} className="rounded-full border border-rose-300/70 bg-rose-500/15 px-3 py-1 transition-all duration-200 hover:-translate-y-0.5 hover:bg-rose-500/25 hover:text-white">
                        {item.skill} · w{item.weight}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div>
                <h3 className="font-display font-medium">Matched Skills</h3>
                {(result.score?.matched_skills || []).length === 0 ? (
                  <p className="mt-2 text-sm text-amber-200">No strong semantic matches found.</p>
                ) : (
                  <ul className="mt-2 flex flex-wrap justify-center gap-2 text-sm text-white/95 md:justify-start">
                    {(result.score?.matched_skills || []).map((item) => (
                      <li key={item.skill} className="rounded-full border border-emerald-300/70 bg-emerald-500/15 px-3 py-1 transition-all duration-200 hover:-translate-y-0.5 hover:bg-emerald-500/25 hover:text-white">
                        {item.skill} · +{item.contribution}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="mt-5">
              <h3 className="font-display font-medium">Deterministic Explanations</h3>
              <ul className="mt-2 space-y-2 text-left text-sm text-white/95">
                {(result.score?.explanations || []).map((text, index) => (
                  <li key={index} className="rounded-lg border border-white/20 bg-black/20 p-3 transition-all duration-200 hover:border-white/45 hover:bg-black/35">
                    {text}
                  </li>
                ))}
              </ul>
            </div>

            {result.inputs?.job_skills_normalized?.length ? (
              <div className="mt-5 text-left">
                <h3 className="font-display font-medium">Parsed Job Skills</h3>
                <ul className="mt-2 flex flex-wrap gap-2 text-sm text-white/95">
                  {result.inputs.job_skills_normalized.map((skill) => (
                    <li key={skill} className="rounded-full border border-white/30 bg-black/25 px-3 py-1 transition-all duration-200 hover:-translate-y-0.5 hover:border-white/60 hover:bg-black/40">
                      {skill}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </section>
        ) : null}
      </div>
    </main>
  );
}
