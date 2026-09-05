"""Motor de scoring.

Recorre cada vacante, busca los términos configurados en config.yaml
(positivos y negativos) sobre el título + descripción normalizados, y
acumula el score. También aplica el bono de salario mínimo si la
fuente trae salario numérico (por ahora solo Adzuna lo da).
"""
from src.job import Job
from src.filters.job_filter import normalize, contains_term


def score_job(job: Job, scoring_cfg: dict, min_salary_mxn: float) -> Job:
    haystack = normalize(f"{job.title} {job.description}")
    total = 0
    matched = []

    for rule in scoring_cfg.get("positive", []):
        if contains_term(haystack, rule["term"]):
            total += rule["points"]
            matched.append(f"+{rule['points']} {rule['term']}")

    for rule in scoring_cfg.get("negative", []):
        if contains_term(haystack, rule["term"]):
            total += rule["points"]  # points ya es negativo en config
            matched.append(f"{rule['points']} {rule['term']}")

    if job.salary_min_mxn:
        salary_min_mensual = job.salary_min_mxn / 12
        if salary_min_mensual >= min_salary_mxn:
            total += 5
            matched.append(f"+5 salario >= {min_salary_mxn}/mes")

    job.score = total
    job.matched_keywords = matched
    return job


def score_all(jobs: list[Job], scoring_cfg: dict, min_salary_mxn: float) -> list[Job]:
    return [score_job(j, scoring_cfg, min_salary_mxn) for j in jobs]
