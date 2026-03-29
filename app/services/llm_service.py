"""
LLM Service
Centralised Mistral AI interface with retry logic, structured JSON parsing,
and graceful error handling.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage

from prompts.analysis_prompts import ANALYSIS_SYSTEM_PROMPT, get_analysis_user_prompt
from prompts.improvement_prompts import IMPROVEMENT_SYSTEM_PROMPT, get_improvement_user_prompt
from prompts.interview_prompts import INTERVIEW_SYSTEM_PROMPT, get_interview_user_prompt

logger = logging.getLogger(__name__)

# ── Default fallback structures ────────────────────────────────────────────────

_DEFAULT_ANALYSIS: dict = {
    "ats_score": 0,
    "job_match_percentage": 0,
    "section_scores": {
        "experience": 0, "skills": 0, "education": 0,
        "formatting": 0, "keywords": 0,
    },
    "strengths": [],
    "weaknesses": [],
    "existing_skills": [],
    "missing_skills": [],
    "suggestions": [],
}

_DEFAULT_INTERVIEW: dict = {
    "technical": [],
    "behavioral": [],
    "scenario": [],
}


class LLMService:
    """Singleton-style service that wraps ChatMistralAI with retry & JSON parsing."""

    MAX_RETRIES = 3
    RETRY_DELAY = 2.0          # seconds (doubles on each retry)
    MODEL       = "mistral-small"
    TEMPERATURE = 0.3          # lower = more consistent JSON output

    def __init__(self) -> None:
        api_key = os.getenv("MISTRAL_API_KEY", "")
        self._llm = ChatMistralAI(
            model=self.MODEL,
            temperature=self.TEMPERATURE,
            mistral_api_key=api_key,
            max_retries=1,           # handled manually below
        )

    # ── Core invoke with retry ─────────────────────────────────────────────────

    def _invoke(self, system: str, user: str) -> tuple[str, str | None]:
        """
        Call the LLM with a system + user message.
        Returns (content, error_message).
        """
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        delay = self.RETRY_DELAY
        last_error: str = ""

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self._llm.invoke(messages)
                return response.content, None
            except Exception as exc:
                last_error = str(exc)
                logger.warning("LLM attempt %d/%d failed: %s", attempt, self.MAX_RETRIES, exc)
                if attempt < self.MAX_RETRIES:
                    time.sleep(delay)
                    delay *= 2   # exponential back-off

        return "", f"LLM error after {self.MAX_RETRIES} retries: {last_error}"

    # ── JSON extraction ────────────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """
        Robustly extract a JSON object from an LLM response that may contain
        prose, markdown fences, or stray characters.
        """
        # 1. Strip ```json ... ``` fences
        cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()

        # 2. Try to find the first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

        # 3. Last resort: try the whole cleaned string
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    # ── Public API ─────────────────────────────────────────────────────────────

    def analyze_resume(
        self,
        resume_text: str,
        job_desc: str,
        role: str = "Software Engineer",
    ) -> tuple[dict, str | None]:
        """
        Analyse a resume against a job description.
        Returns (result_dict, error_or_None).
        """
        user_prompt = get_analysis_user_prompt(resume_text, job_desc, role)
        raw, error  = self._invoke(ANALYSIS_SYSTEM_PROMPT, user_prompt)

        if error:
            return _DEFAULT_ANALYSIS, error

        parsed = self._extract_json(raw)
        if not parsed:
            logger.error("Failed to parse analysis JSON. Raw: %s", raw[:500])
            return _DEFAULT_ANALYSIS, "Could not parse AI response. Please try again."

        # Merge with defaults to fill any missing keys
        result = {**_DEFAULT_ANALYSIS, **parsed}

        # Clamp scores to [0, 100]
        result["ats_score"]            = max(0, min(100, int(result.get("ats_score", 0))))
        result["job_match_percentage"] = max(0, min(100, int(result.get("job_match_percentage", 0))))

        sec = result.get("section_scores", {})
        result["section_scores"] = {
            k: max(0, min(100, int(v)))
            for k, v in sec.items()
        }

        return result, None

    def improve_resume(
        self,
        resume_text: str,
        job_desc: str,
        role: str = "Software Engineer",
    ) -> tuple[str, str | None]:
        """
        Rewrite the resume to better match the job description.
        Returns (improved_text, error_or_None).
        """
        user_prompt = get_improvement_user_prompt(resume_text, job_desc, role)
        raw, error  = self._invoke(IMPROVEMENT_SYSTEM_PROMPT, user_prompt)

        if error:
            return "", error

        return raw.strip(), None

    def generate_interview_questions(
        self,
        resume_text: str,
        job_desc: str,
        role: str = "Software Engineer",
    ) -> tuple[dict, str | None]:
        """
        Generate structured interview questions.
        Returns (questions_dict, error_or_None).
        """
        user_prompt = get_interview_user_prompt(resume_text, job_desc, role)
        raw, error  = self._invoke(INTERVIEW_SYSTEM_PROMPT, user_prompt)

        if error:
            return _DEFAULT_INTERVIEW, error

        parsed = self._extract_json(raw)
        if not parsed:
            logger.error("Failed to parse interview JSON. Raw: %s", raw[:500])
            return _DEFAULT_INTERVIEW, "Could not parse AI response. Please try again."

        result = {**_DEFAULT_INTERVIEW, **parsed}
        return result, None
