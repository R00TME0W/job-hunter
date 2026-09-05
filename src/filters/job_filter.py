"""Normalización de texto y exclusiones duras.

Normalizamos (minúsculas + sin acentos) antes de cualquier match para
no perder coincidencias por mayúsculas/acentos, y usamos límites de
palabra (regex \\b) para que 'siem' no matchee dentro de otra palabra.
"""
import re
import unicodedata

from src.job import Job


def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def contains_term(haystack_normalized: str, term: str) -> bool:
    term_normalized = normalize(term)
    pattern = r"\b" + re.escape(term_normalized) + r"\b"
    return re.search(pattern, haystack_normalized) is not None


def apply_hard_excludes(jobs: list[Job], hard_excludes: list[str]) -> list[Job]:
    kept = []
    for job in jobs:
        haystack = normalize(f"{job.title} {job.description}")
        if any(contains_term(haystack, term) for term in hard_excludes):
            continue
        kept.append(job)
    return kept


def deduplicate(jobs: list[Job]) -> list[Job]:
    seen = set()
    unique = []
    for job in jobs:
        if job.job_id in seen:
            continue
        seen.add(job.job_id)
        unique.append(job)
    return unique
