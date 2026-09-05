"""Imprime el reporte en consola, en el formato tipo tarjeta:

Junior SOC Analyst
Score: 92/100
--------------------------------
📍 Remoto - México
💰 $18,000 - $22,000 MXN
🏢 Empresa X

✓ Cybersecurity
✓ Networking
✓ Linux
✓ SIEM
✓ Junior

Aplicar: <url>
"""
from src.job import Job

MAX_SCORE_FOR_DISPLAY = 100  # solo para el "/100" visual, el score real no tiene tope


def print_report(jobs: list[Job], min_score: int) -> None:
    shown = [j for j in jobs if j.score >= min_score]
    shown.sort(key=lambda j: j.score, reverse=True)

    if not shown:
        print(f"No hay vacantes con score >= {min_score} en esta corrida.")
        return

    for job in shown:
        display_score = min(job.score, MAX_SCORE_FOR_DISPLAY)
        print(job.title)
        print(f"Score: {display_score}/{MAX_SCORE_FOR_DISPLAY}")
        print("-" * 32)
        if job.location:
            print(f"📍 {job.location}")
        if job.salary_text:
            print(f"💰 {job.salary_text}")
        if job.company:
            print(f"🏢 {job.company}")
        print()
        for match in job.matched_keywords:
            marker = "✓" if not match.startswith("-") else "✗"
            print(f"{marker} {match}")
        print()
        print(f"Aplicar: {job.url}")
        print("=" * 40)
        print()

    print(f"Total: {len(shown)} vacante(s) con score >= {min_score}")
