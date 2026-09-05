"""Enlaces de búsqueda directa (sin scraping, sin login).

En vez de leer el contenido de LinkedIn/Indeed/OCC/Computrabajo (lo
cual violaría sus términos de servicio y arriesga que te bloqueen la
cuenta o la IP), este módulo solo ARMA la URL de búsqueda ya
rellenada con tu término + ubicación. Tú le das clic y navegas ahí
manualmente — cero riesgo de baneo porque no se automatiza nada
dentro de esos sitios.

Nota: los formatos de URL de OCC y Computrabajo están basados en
patrones públicos conocidos de sus sitios; si algún día cambian su
estructura, el peor caso es que el link te mande a una búsqueda
genérica en vez de la exacta.
"""
import unicodedata
from urllib.parse import quote_plus


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace(" ", "-")
    return text


def linkedin_link(term: str, location: str) -> str:
    return (
        "https://www.linkedin.com/jobs/search/?"
        f"keywords={quote_plus(term)}&location={quote_plus(location)}"
    )


def indeed_link(term: str, location: str) -> str:
    return (
        "https://mx.indeed.com/jobs?"
        f"q={quote_plus(term)}&l={quote_plus(location)}"
    )


def occ_link(term: str, location: str) -> str:
    return f"https://www.occ.com.mx/empleos/de-{_slugify(term)}/en-{_slugify(location)}/"


def computrabajo_link(term: str, location: str) -> str:
    return f"https://mx.computrabajo.com/trabajo-de-{_slugify(term)}-en-{_slugify(location)}"


PLATFORM_BUILDERS = {
    "linkedin": linkedin_link,
    "indeed": indeed_link,
    "occ": occ_link,
    "computrabajo": computrabajo_link,
}


def build_links(platforms_cfg: dict, search_terms: list[str], locations: list[str]) -> list[dict]:
    """Devuelve una lista de {platform, term, location, url} para cada
    combinación, solo de las plataformas habilitadas en platforms_cfg."""
    links = []
    if not locations:
        locations = [""]

    for platform, builder in PLATFORM_BUILDERS.items():
        if not platforms_cfg.get(platform, {}).get("enabled"):
            continue
        for term in search_terms:
            for location in locations:
                links.append({
                    "platform": platform,
                    "term": term,
                    "location": location,
                    "url": builder(term, location or "México"),
                })
    return links


def print_links(links: list[dict]) -> None:
    if not links:
        return
    print("\n🔗 Enlaces de búsqueda directa (revisar manualmente):")
    print("=" * 40)
    by_platform: dict[str, list[dict]] = {}
    for link in links:
        by_platform.setdefault(link["platform"], []).append(link)

    for platform, items in by_platform.items():
        print(f"\n{platform.upper()}:")
        for item in items:
            label = item["term"] + (f" — {item['location']}" if item["location"] else "")
            print(f"  {label}: {item['url']}")


def format_links_message(links: list[dict], max_per_platform: int = 5) -> str:
    """Arma UN solo mensaje de texto con los links agrupados por
    plataforma, recortado a max_per_platform por plataforma para no
    generar un mensaje gigante en Telegram."""
    if not links:
        return ""

    by_platform: dict[str, list[dict]] = {}
    for link in links:
        by_platform.setdefault(link["platform"], []).append(link)

    lines = ["🔗 *Enlaces de búsqueda directa*"]
    for platform, items in by_platform.items():
        lines.append(f"\n*{platform.upper()}*")
        for item in items[:max_per_platform]:
            label = item["term"] + (f" — {item['location']}" if item["location"] else "")
            lines.append(f"[{label}]({item['url']})")
        remaining = len(items) - max_per_platform
        if remaining > 0:
            lines.append(f"...y {remaining} más (revisa la consola)")

    return "\n".join(lines)
