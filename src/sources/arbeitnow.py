"""Fuente: Arbeitnow Job Board API (https://www.arbeitnow.com/api/job-board-api)

API pública y gratuita, sin API key. Trae vacantes remotas y
presenciales de varias fuentes. No soporta filtro por término en la
URL, así que traemos todo (paginado) y filtramos localmente por los
search_terms configurados.
"""
import requests
from src.job import Job

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch(search_terms: list[str], max_pages: int = 3, timeout: int = 15) -> list[Job]:
    terms_lower = [t.lower() for t in search_terms]
    jobs: list[Job] = []
    url = BASE_URL

    for _ in range(max_pages):
        if not url:
            break
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[arbeitnow] error: {e}")
            break

        payload = resp.json()
        for item in payload.get("data", []):
            haystack = f"{item.get('title', '')} {item.get('description', '')}".lower()
            if not any(term in haystack for term in terms_lower):
                continue
            jobs.append(
                Job(
                    title=item.get("title", ""),
                    company=item.get("company_name", ""),
                    location=item.get("location", "") or (
                        "Remoto" if item.get("remote") else ""
                    ),
                    salary_text="",
                    description=item.get("description", "") or "",
                    url=item.get("url", ""),
                    source="arbeitnow",
                )
            )

        # la API pagina vía 'links.next'
        url = (payload.get("links") or {}).get("next")

    return jobs
