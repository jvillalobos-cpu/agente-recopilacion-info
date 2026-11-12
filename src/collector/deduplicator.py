from difflib import SequenceMatcher
from typing import List
from src.models import NewsItem

TITLE_SIMILARITY_THRESHOLD = 0.78


def _normalize_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def deduplicate_items(items: List[NewsItem]) -> List[NewsItem]:
    """
    Elimina notas duplicadas de una misma categoría: por URL exacta (normalizada) o por
    similitud de título por encima del umbral, para evitar que dos fuentes que cubren el
    mismo hecho aparezcan dos veces en el boletín.
    """
    kept: List[NewsItem] = []
    seen_urls = set()

    for item in items:
        normalized_url = _normalize_url(item.url)
        if normalized_url in seen_urls:
            continue

        is_duplicate = any(
            _title_similarity(item.title, existing.title) >= TITLE_SIMILARITY_THRESHOLD
            for existing in kept
        )
        if is_duplicate:
            continue

        kept.append(item)
        seen_urls.add(normalized_url)

    return kept
