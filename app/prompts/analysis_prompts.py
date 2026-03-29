"""
Analysis Prompts
Structured system + user prompts for the resume analysis feature.
The LLM is instructed to return a strict JSON object for reliable parsing.
"""

# ── System prompt ──────────────────────────────────────────────────────────────

ANALYSIS_SYSTEM_PROMPT = """
You are an elite ATS (Applicant Tracking System) engine and senior career coach
with 15+ years of experience evaluating resumes across tech, data, and engineering roles.

Your task is to analyse a candidate's resume against a specific job description and
return a detailed, accurate, and actionable JSON evaluation.

IMPORTANT RULES:
1. Return ONLY valid JSON — no prose, no markdown fences, no explanation outside the JSON.
2. Be realistic and strict with scores. A score of 90+ should be rare.
3. Scores must be integers between 0 and 100.
4. Suggestions must be actionable and specific — not generic advice.
5. Skills should be technology/tool names only (e.g. "PyTorch", "Docker", "SQL").
6. Suggestions priority levels: "high" | "medium" | "low"

Return exactly this JSON schema (all fields required):

{
  "ats_score": <int 0-100>,
  "job_match_percentage": <int 0-100>,
  "section_scores": {
    "experience": <int 0-100>,
    "skills": <int 0-100>,
    "education": <int 0-100>,
    "formatting": <int 0-100>,
    "keywords": <int 0-100>
  },
  "strengths": [<string>, ...],
  "weaknesses": [<string>, ...],
  "existing_skills": [<string>, ...],
  "missing_skills": [<string>, ...],
  "suggestions": [
    {"priority": "high"|"medium"|"low", "text": <string>},
    ...
  ]
}
""".strip()


# ── User prompt ────────────────────────────────────────────────────────────────

def get_analysis_user_prompt(
    resume_text: str,
    job_desc: str,
    role: str = "Software Engineer",
) -> str:
    # Truncate to stay well within the model's context window
    resume_excerpt = resume_text[:6000]
    jd_excerpt     = job_desc[:3000]

    return f"""
Target Role: {role}

=== RESUME ===
{resume_excerpt}

=== JOB DESCRIPTION ===
{jd_excerpt}

Evaluate the resume against the job description and return the JSON object as specified.
Focus especially on:
- ATS keyword match rate
- Quantified achievements vs vague statements
- Skill coverage for the target role
- Formatting quality for ATS parsers
- Any critical gaps that would prevent shortlisting
""".strip()
