"""Representación normalizada de una vacante, sin importar de qué
fuente venga (Remotive, Arbeitnow, Adzuna, la que agregues después)."""
from dataclasses import dataclass, field
import hashlib


@dataclass
class Job:
    title: str
    company: str
    location: str
    salary_text: str
    description: str
    url: str
    source: str
    salary_min_mxn: float | None = None
    score: int = 0
    matched_keywords: list[str] = field(default_factory=list)

    @property
    def job_id(self) -> str:
        """Id estable para deduplicar entre fuentes/corridas."""
        raw = f"{self.title}|{self.company}|{self.source}".lower().strip()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
