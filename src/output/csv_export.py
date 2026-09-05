"""Exporta las vacantes puntuadas a data/jobs.csv, acumulando entre
corridas (no sobrescribe) y evitando duplicados por job_id."""
import csv
import pathlib
from datetime import datetime

from src.job import Job

FIELDNAMES = [
    "job_id", "score", "title", "company", "location",
    "salary_text", "source", "url", "matched_keywords",
]


def export(jobs: list[Job], path: pathlib.Path) -> int:
    """Devuelve cuántas vacantes NUEVAS se agregaron."""
    existing_ids = set()
    if path.exists():
        with open(path, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                existing_ids.add(row["job_id"])

    new_jobs = [j for j in jobs if j.job_id not in existing_ids]
    if not new_jobs:
        return 0

    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        for job in new_jobs:
            writer.writerow({
                "job_id": job.job_id,
                "score": job.score,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_text": job.salary_text,
                "source": job.source,
                "url": job.url,
                "matched_keywords": "; ".join(job.matched_keywords),
            })
    return len(new_jobs)


LINKS_FIELDNAMES = ["run_date", "platform", "term", "location", "url"]


def export_links(links: list[dict], path: pathlib.Path) -> int:
    """Exporta los enlaces de búsqueda directa (LinkedIn/Indeed/OCC/
    Computrabajo) a su propio CSV, con la fecha de la corrida. No
    deduplica entre corridas a propósito: así puedes ver en el CSV
    cuántas veces se generó cada búsqueda y cuándo, útil si luego
    quieres hacer análisis de frecuencia."""
    if not links:
        return 0

    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LINKS_FIELDNAMES)
        if write_header:
            writer.writeheader()
        for link in links:
            writer.writerow({
                "run_date": run_date,
                "platform": link["platform"],
                "term": link["term"],
                "location": link["location"],
                "url": link["url"],
            })
    return len(links)
