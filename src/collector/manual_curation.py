import json
from typing import Dict, List
from src.models import NewsItem
from src.collector.whitelist_validator import WhitelistValidator

VALID_CATEGORIES = {
    "nota_principal", "competencia", "sector_publico_salud",
    "canales_informacion", "sector_privado_salud", "ia_salud_laboratorios"
}


class ManualCurationCollector:
    """
    Recolector de notas curadas a mano, pensado para posts de redes sociales
    (Instagram, X, LinkedIn) donde una persona o empresa de interés publica
    directamente y no tiene blog/sala de prensa propia. No hay scraping ni
    API automatizada: el analista registra cada post en config/manual_posts.json
    con su URL, tema y fecha reales, y este collector lo integra al pipeline
    con las mismas reglas de guardrail que cualquier otra fuente (lista
    blanca + fecha verificable para el filtro de recencia).
    """

    def __init__(self, posts_file_path: str = "config/manual_posts.json"):
        self.posts_file_path = posts_file_path
        self.validator = WhitelistValidator()

    def fetch_curated_posts(self) -> Dict[str, List[NewsItem]]:
        """Carga y valida las entradas de config/manual_posts.json, agrupadas por categoría."""
        by_category: Dict[str, List[NewsItem]] = {cat: [] for cat in VALID_CATEGORIES}

        try:
            with open(self.posts_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return by_category
        except json.JSONDecodeError as e:
            print(f"[WARN] {self.posts_file_path} tiene JSON inválido ({e}). Se omite la curación manual.")
            return by_category

        for entry in data.get("posts", []):
            title = entry.get("title", "")
            url = entry.get("url", "")
            category = entry.get("category", "")

            if title.strip().lower().startswith("ejemplo") or "EJEMPLO" in url:
                continue  # fila de plantilla, no es una nota real

            if category not in VALID_CATEGORIES:
                print(f"[WARN] Post manual descartado: categoría inválida o faltante ('{category}') en '{title}'.")
                continue

            if not self.validator.validate_and_log(url, title=title, category=category):
                continue  # ya quedó registrado en el log de seguridad por el validador

            if not entry.get("published_date"):
                print(f"[WARN] Post manual descartado por falta de published_date: '{title}'.")
                continue

            by_category[category].append(NewsItem(
                title=title,
                content=entry.get("content", ""),
                url=url,
                source_domain=entry.get("source_domain", ""),
                category=category,
                published_date=entry.get("published_date"),
            ))

        return by_category
