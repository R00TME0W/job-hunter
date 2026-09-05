"""Orquestador principal.

Uso:
    python -m src.main

Corre todas las fuentes habilitadas en config.yaml, aplica
exclusiones duras, deduplica, puntúa, guarda en data/jobs.csv
(acumulado, sin duplicados), manda notificación por Telegram si está
activa, genera enlaces de búsqueda directa (LinkedIn/Indeed/OCC/
Computrabajo) y los exporta a data/quick_links.csv.
"""
import pathlib

from src.config import load_config
from src.job import Job
from src.sources import remotive, arbeitnow, adzuna
from src.sources.quick_links import build_links, print_links, format_links_message
from src.filters.job_filter import apply_hard_excludes, deduplicate
from src.scoring.matcher import score_all
from src.output.csv_export import export, export_links
from src.output.report import print_report
from src.output.telegram_notify import notify, send_text

DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "jobs.csv"
LINKS_DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "quick_links.csv"


def collect_jobs(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    sources_cfg = cfg["sources"]

    if sources_cfg["remotive"]["enabled"]:
        print("Buscando en Remotive...")
        jobs += remotive.fetch(sources_cfg["remotive"]["search_terms"])

    if sources_cfg["arbeitnow"]["enabled"]:
        print("Buscando en Arbeitnow...")
        jobs += arbeitnow.fetch(sources_cfg["arbeitnow"]["search_terms"])

    if sources_cfg["adzuna"]["enabled"]:
        print("Buscando en Adzuna...")
        adz = sources_cfg["adzuna"]
        jobs += adzuna.fetch(
            search_terms=adz["search_terms"],
            country=adz["country"],
            app_id=adz["app_id"],
            app_key=adz["app_key"],
            locations=adz.get("locations", []),
        )

    return jobs


def main() -> None:
    cfg = load_config()
    sources_cfg = cfg["sources"]

    jobs = collect_jobs(cfg)
    print(f"\n{len(jobs)} vacantes encontradas antes de filtrar.")

    jobs = deduplicate(jobs)
    jobs = apply_hard_excludes(jobs, cfg.get("hard_excludes", []))
    jobs = score_all(jobs, cfg["scoring"], cfg.get("min_salary_mxn", 0))

    added = export(jobs, DATA_PATH)
    print(f"{added} vacantes nuevas agregadas a {DATA_PATH}")

    print()
    print_report(jobs, cfg.get("min_score", 40))

    tg = cfg.get("telegram", {})
    if tg.get("enabled"):
        sent = notify(jobs, cfg.get("min_score", 40), tg.get("bot_token", ""), tg.get("chat_id", ""))
        print(f"{sent} notificación(es) enviada(s) por Telegram")

    adz = sources_cfg.get("adzuna", {})
    links = build_links(
        platforms_cfg=sources_cfg,
        search_terms=adz.get("search_terms", []),
        locations=adz.get("locations", []),
    )
    print_links(links)

    links_added = export_links(links, LINKS_DATA_PATH)
    if links_added:
        print(f"\n{links_added} enlaces exportados a {LINKS_DATA_PATH}")

    if tg.get("enabled"):
        links_msg = format_links_message(links)
        if send_text(links_msg, tg.get("bot_token", ""), tg.get("chat_id", "")):
            print("Resumen de enlaces enviado por Telegram")


if __name__ == "__main__":
    main()
