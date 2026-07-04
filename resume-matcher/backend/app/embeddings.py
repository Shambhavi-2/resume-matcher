"""
Stage 1 of the matching pipeline: fast, local text similarity using TF-IDF
instead of neural embeddings. This avoids the torch/sentence-transformers
dependency (which can hit DLL/driver issues on some Windows machines) while
still giving a reasonable "how much does this resume cover this job
requirement" signal based on shared vocabulary and phrasing.
"""
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_resume_against_job(
    resume_chunks: List[str], job_chunks: List[str], top_k: int = 8
) -> Dict[str, Any]:
    if not resume_chunks or not job_chunks:
        return {"score": 0.0, "matches": []}

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    all_chunks = job_chunks + resume_chunks
    tfidf_matrix = vectorizer.fit_transform(all_chunks)

    job_vecs = tfidf_matrix[: len(job_chunks)]
    resume_vecs = tfidf_matrix[len(job_chunks) :]

    sim_matrix = cosine_similarity(job_vecs, resume_vecs)

    matches = []
    per_job_best = []
    for j_idx, row in enumerate(sim_matrix):
        best_r_idx = int(np.argmax(row))
        best_score = float(row[best_r_idx])
        per_job_best.append(best_score)
        matches.append(
            {
                "job_requirement": job_chunks[j_idx],
                "best_resume_match": resume_chunks[best_r_idx],
                "similarity": round(best_score, 4),
            }
        )

    matches.sort(key=lambda m: m["similarity"], reverse=True)

    overall = float(np.mean(per_job_best)) if per_job_best else 0.0
    scaled_score = max(0.0, min(100.0, (overall - 0.05) / (0.45 - 0.05) * 100))

    return {
        "score": round(scaled_score, 1),
        "matches": matches[:top_k],
    }