import json
from src.collector.manual_curation import ManualCurationCollector


def write_posts(tmp_path, posts):
    path = tmp_path / "manual_posts.json"
    path.write_text(json.dumps({"posts": posts}), encoding="utf-8")
    return str(path)


def test_skips_template_example_row():
    collector = ManualCurationCollector(posts_file_path="config/manual_posts.json")
    result = collector.fetch_curated_posts()
    all_titles = [item.title for items in result.values() for item in items]
    assert not any("título breve" in t.lower() for t in all_titles)  # fila de ejemplo omitida


def test_loads_valid_instagram_post(tmp_path):
    path = write_posts(tmp_path, [{
        "entity_name": "Bruno Valera",
        "platform": "Instagram",
        "title": "Bruno Valera anuncia nueva alianza de HealthTech México",
        "content": "Contenido de prueba con dos renglones de detalle real.",
        "url": "https://www.instagram.com/p/REAL123/",
        "source_domain": "instagram.com",
        "category": "canales_informacion",
        "published_date": "2026-09-15"
    }])
    collector = ManualCurationCollector(posts_file_path=path)
    result = collector.fetch_curated_posts()
    assert len(result["canales_informacion"]) == 1
    assert result["canales_informacion"][0].source_domain == "instagram.com"


def test_loads_valid_ia_salud_laboratorios_post(tmp_path):
    path = write_posts(tmp_path, [{
        "entity_name": "YC",
        "platform": "LinkedIn",
        "title": "Startups de IA en diagnóstico clínico",
        "content": "Lista de startups de IA enfocadas en laboratorios clínicos y diagnóstico.",
        "url": "https://www.linkedin.com/posts/example-ia-salud",
        "source_domain": "linkedin.com",
        "category": "ia_salud_laboratorios",
        "published_date": "2026-10-29"
    }])
    collector = ManualCurationCollector(posts_file_path=path)
    result = collector.fetch_curated_posts()
    assert len(result["ia_salud_laboratorios"]) == 1


def test_rejects_post_without_published_date(tmp_path):
    path = write_posts(tmp_path, [{
        "title": "Post sin fecha",
        "content": "Contenido de prueba.",
        "url": "https://www.instagram.com/p/SINFECHA/",
        "source_domain": "instagram.com",
        "category": "canales_informacion"
    }])
    collector = ManualCurationCollector(posts_file_path=path)
    result = collector.fetch_curated_posts()
    assert len(result["canales_informacion"]) == 0


def test_rejects_post_with_invalid_category(tmp_path):
    path = write_posts(tmp_path, [{
        "title": "Post con categoría inválida",
        "content": "Contenido de prueba.",
        "url": "https://www.instagram.com/p/CATINVALIDA/",
        "source_domain": "instagram.com",
        "category": "categoria_inventada",
        "published_date": "2026-09-15"
    }])
    collector = ManualCurationCollector(posts_file_path=path)
    result = collector.fetch_curated_posts()
    assert sum(len(v) for v in result.values()) == 0


def test_rejects_post_from_non_whitelisted_domain(tmp_path):
    path = write_posts(tmp_path, [{
        "title": "Post de dominio no autorizado",
        "content": "Contenido de prueba.",
        "url": "https://www.tiktok.com/@alguien/video/123",
        "source_domain": "tiktok.com",
        "category": "canales_informacion",
        "published_date": "2026-09-15"
    }])
    collector = ManualCurationCollector(posts_file_path=path)
    result = collector.fetch_curated_posts()
    assert len(result["canales_informacion"]) == 0


def test_missing_file_returns_empty_categories():
    collector = ManualCurationCollector(posts_file_path="config/no_existe.json")
    result = collector.fetch_curated_posts()
    assert sum(len(v) for v in result.values()) == 0
