"""Notificación por Telegram.

Manda un mensaje por cada vacante que pase min_score, usando la API
oficial de Bots de Telegram (gratis, sin límites prácticos para este
volumen). No requiere librería extra, solo requests.

Cómo activar:
  1. Habla con @BotFather en Telegram, /newbot, sigue los pasos.
     Te da un bot_token tipo "123456:ABC-DEF...".
  2. Mándale cualquier mensaje a tu bot recién creado.
  3. Visita https://api.telegram.org/bot<TOKEN>/getUpdates en el
     navegador y copia el valor de "chat":{"id": ...} -> ese es tu
     chat_id.
  4. Pon ambos en config.yaml (sección 'telegram') y enabled: true.
"""
import requests
from src.job import Job

API_URL_TMPL = "https://api.telegram.org/bot{token}/sendMessage"
MAX_JOBS_PER_RUN = 15  # evita floodear el chat si un día hay muchas


def _format_message(job: Job) -> str:
    lines = [
        f"*{job.title}*",
        f"Score: {job.score}",
    ]
    if job.company:
        lines.append(f"🏢 {job.company}")
    if job.location:
        lines.append(f"📍 {job.location}")
    if job.salary_text:
        lines.append(f"💰 {job.salary_text}")
    lines.append(f"[Aplicar]({job.url})")
    return "\n".join(lines)


def send_text(text: str, bot_token: str, chat_id: str) -> bool:
    """Manda un solo mensaje de texto libre (para el resumen de links)."""
    if not bot_token or not chat_id or not text:
        return False
    url = API_URL_TMPL.format(token=bot_token)
    try:
        resp = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[telegram] error mandando resumen de links: {e}")
        return False


def notify(jobs: list[Job], min_score: int, bot_token: str, chat_id: str) -> int:
    if not bot_token or not chat_id:
        print("[telegram] falta bot_token / chat_id en config.yaml — se omite notificación")
        return 0

    to_send = [j for j in jobs if j.score >= min_score]
    to_send.sort(key=lambda j: j.score, reverse=True)
    to_send = to_send[:MAX_JOBS_PER_RUN]

    url = API_URL_TMPL.format(token=bot_token)
    sent = 0
    for job in to_send:
        try:
            resp = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": _format_message(job),
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )
            resp.raise_for_status()
            sent += 1
        except requests.RequestException as e:
            print(f"[telegram] error mandando '{job.title}': {e}")

    return sent
