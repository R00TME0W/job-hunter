"""Fuente: Adzuna Job Search API (https://developer.adzuna.com)

API oficial y gratuita (tier gratis: ~1000 requests/mes), pero
requiere registrarte para obtener app_id + app_key:
  1. Crea cuenta en https://developer.adzuna.com/
  2. Copia tu app_id y app_key a config.yaml (sources.adzuna)
  3. Pon sources.adzuna.enabled: true

Cubre México (country='mx'), lo que la hace la mejor fuente para
vacantes locales en Hermosillo / México en general.
"""
import requests
from src.job import Job

BASE_URL_TMPL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


def fetch(
    search_terms: list[str],
    country: str,
    app_id: str,
    app_key: str,
    locations: list[str] | None = None,
    results_per_page: int = 20,
    timeout: int = 15,
) -> list[Job]:
    if not app_id or not app_key:
        print("[adzuna] falta app_id / app_key en config.yaml — se omite esta fuente")
        return []

    jobs: list[Job] = []
    url = BASE_URL_TMPL.format(country=country)

    if not locations:
        locations = [""]

    for term in search_terms:
        for location in locations:
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "what": term,
                "results_per_page": results_per_page,
                "content-type": "application/json",
            }

            if location:
                params["where"] = location

            try:
                resp = requests.get(url, params=params, timeout=timeout)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"[adzuna] error buscando '{term}' en '{location}': {e}")
                continue

            for item in resp.json().get("results", []):
                salary_min = item.get("salary_min")
                jobs.append(
                    Job(
                        title=item.get("title", ""),
                        company=(item.get("company") or {}).get("display_name", ""),
                        location=(item.get("location") or {}).get("display_name", ""),
                        salary_text=(
                            f"{salary_min}-{item.get('salary_max')}"
                            if salary_min
                            else ""
                        ),
                        description=item.get("description", "") or "",
                        url=item.get("redirect_url", ""),
                        source="adzuna",
                        salary_min_mxn=salary_min,
                    )
                )

    return jobs
