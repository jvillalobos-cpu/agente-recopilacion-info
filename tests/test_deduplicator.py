from src.models import NewsItem
from src.collector.deduplicator import deduplicate_items


def make_item(title, url):
    return NewsItem(
        title=title, content="Contenido de prueba.", url=url,
        source_domain="gob.mx", category="sector_publico_salud", published_date="2026-10-20"
    )


def test_removes_exact_duplicate_url():
    items = [
        make_item("Nota A", "https://www.gob.mx/salud/a"),
        make_item("Nota A (repetida)", "https://www.gob.mx/salud/a"),
    ]
    assert len(deduplicate_items(items)) == 1


def test_removes_near_duplicate_title():
    items = [
        make_item("IMSS eleva a 8% el incremento salarial de sus trabajadores", "https://www.gob.mx/salud/a"),
        make_item("IMSS eleva a 8 por ciento el incremento salarial de trabajadores", "https://www.gob.mx/salud/b"),
    ]
    assert len(deduplicate_items(items)) == 1


def test_keeps_genuinely_different_notes():
    items = [
        make_item("COFEPRIS autoriza nueva vacuna contra el dengue", "https://www.gob.mx/salud/a"),
        make_item("IMSS inaugura hospital en Rosarito", "https://www.gob.mx/salud/b"),
    ]
    assert len(deduplicate_items(items)) == 2
