"""Fuente: Remotive (https://remotive.com/api/remote-jobs)

API pública y gratuita, sin necesidad de API key. Devuelve vacantes
remotas. Un solo request trae todo el catálogo filtrado por 'search',
así que hacemos un request por término de búsqueda configurado.
"""
import requests
from src.job import Job

BASE_URL = "https://remotive.com/api/remote-jobs"


def fetch(search_terms: list[str], timeout: int = 15) -> list[Job]:
    jobs: list[Job] = []
    for term in search_terms:
        try:
            resp = requests.get(
                BASE_URL, params={"search": term}, timeout=timeout
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[remotive] error buscando '{term}': {e}")
            continue

        for item in resp.json().get("jobs", []):
            jobs.append(
                Job(
                    title=item.get("title", ""),
                    company=item.get("company_name", ""),
                    location=item.get("candidate_required_location", ""),
                    salary_text=item.get("salary", "") or "",
                    description=item.get("description", "") or "",
                    url=item.get("url", ""),
                    source="remotive",
                )
            )
    return jobs
