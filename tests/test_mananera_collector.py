import datetime
from src.collector.mananera_collector import MananeraSaludCollector


def test_most_recent_tuesday_when_today_is_tuesday():
    collector = MananeraSaludCollector()
    tuesday = datetime.date(2026, 10, 27)  # martes
    assert collector._most_recent_tuesday(tuesday) == tuesday


def test_most_recent_tuesday_when_today_is_later_in_week():
    collector = MananeraSaludCollector()
    friday = datetime.date(2026, 10, 30)
    assert collector._most_recent_tuesday(friday) == datetime.date(2026, 10, 27)


def test_most_recent_tuesday_when_today_is_monday():
    collector = MananeraSaludCollector()
    monday = datetime.date(2026, 11, 2)
    assert collector._most_recent_tuesday(monday) == datetime.date(2026, 10, 27)


def test_extract_health_excerpt_finds_imss_mention():
    collector = MananeraSaludCollector()
    text = "<p>Tema de agua.</p><p>Hoy hablamos del IMSS y el plan de doce acciones.</p>"
    excerpt = collector._extract_health_excerpt(text)
    assert excerpt is not None
    assert "IMSS" in excerpt or "imss" in excerpt.lower()


def test_extract_health_excerpt_returns_none_without_keywords():
    collector = MananeraSaludCollector()
    text = "<p>Hoy hablamos de infraestructura carretera y agua potable.</p>"
    assert collector._extract_health_excerpt(text) is None


def test_fetch_falls_back_to_mock_without_network():
    collector = MananeraSaludCollector()
    items = collector.fetch_latest_tuesday_health_block(reference_date=datetime.date(2026, 10, 27))
    assert len(items) == 1
    assert items[0].title.startswith("[MOCK]")
    assert items[0].category == "sector_publico_salud"
    assert items[0].source_domain == "gob.mx"
    assert items[0].published_date == "2026-10-27"
