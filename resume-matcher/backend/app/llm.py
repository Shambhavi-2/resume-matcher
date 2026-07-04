"""
Stage 2 of the matching pipeline: an LLM reasons only over the chunks that
stage 1 (embeddings) already flagged as relevant, and turns raw similarity
scores into a human-readable explanation. If no API key is configured, the
app degrades gracefully to a heuristic explanation instead of failing.
"""
import json
from typing import Dict, Any, List

from openai import OpenAI
from .config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a careful, specific career coach. You will be given a list of
job requirements paired with the resume snippet that best matches each one, along with a
similarity score from 0 to 1 (higher = stronger match). Using ONLY this evidence:

1. List 3-5 genuine strengths (requirements the resume covers well - similarity roughly above 0.55).
2. List 3-5 gaps (requirements with weak or no resume evidence - similarity roughly below 0.4).
3. Suggest 3-5 concrete, specific rewrites or additions the candidate could make to their
   resume to close the gaps. Be specific to the actual text given, not generic advice.

Respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{"strengths": ["..."], "gaps": ["..."], "suggestions": ["..."]}
"""


def generate_explanation(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not settings.openai_api_key:
        return _heuristic_explanation(matches)

    client = OpenAI(api_key=settings.openai_api_key)
    evidence = "\n".join(
        f"- Requirement: {m['job_requirement']}\n"
        f"  Best resume match (similarity {m['similarity']}): {m['best_resume_match']}"
        for m in matches
    )

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": evidence},
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(content)
        return {
            "strengths": parsed.get("strengths", []),
            "gaps": parsed.get("gaps", []),
            "suggestions": parsed.get("suggestions", []),
        }
    except Exception:
        # Never let an LLM hiccup break the match - fall back to the heuristic version.
        return _heuristic_explanation(matches)


def _heuristic_explanation(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pure-embedding fallback used when no LLM key is configured or the call fails."""
    strengths = [
        f"Strong match for \u201c{m['job_requirement'][:80]}\u201d"
        for m in matches
        if m["similarity"] >= 0.55
    ][:5]
    gaps = [
        f"Weak or missing evidence for \u201c{m['job_requirement'][:80]}\u201d"
        for m in matches
        if m["similarity"] < 0.4
    ][:5]
    suggestions = [
        f"Add a specific, quantified example addressing: \u201c{m['job_requirement'][:80]}\u201d"
        for m in matches
        if m["similarity"] < 0.4
    ][:5]
    return {"strengths": strengths, "gaps": gaps, "suggestions": suggestions}
