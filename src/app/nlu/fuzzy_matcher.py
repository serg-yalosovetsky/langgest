from __future__ import annotations

from difflib import SequenceMatcher


def ratio(a: str, b: str) -> float:
    """Return similarity ratio in [0, 1] between two strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def best_match(query: str, candidates: list[str], threshold: float = 0.70) -> tuple[str, float] | None:
    """Return (best_candidate, score) if best score >= threshold, else None."""
    if not candidates:
        return None

    best_score = 0.0
    best_cand = ""
    for cand in candidates:
        score = ratio(query, cand)
        if score > best_score:
            best_score = score
            best_cand = cand

    if best_score >= threshold:
        return best_cand, best_score
    return None
