import datetime
from src.models import NewsItem
from src.collector.recency_filter import is_recent, filter_recent_items, is_in_current_month, filter_items_in_current_month


def make_item(published_date=None):
    return NewsItem(
        title="Nota de prueba", content="Contenido de prueba.",
        url="https://www.gob.mx/salud/nota", source_domain="gob.mx",
        category="sector_publico_salud", published_date=published_date
    )


def test_item_within_window_is_recent():
    ref = datetime.date(2026, 10, 30)
    item = make_item(published_date="2026-10-20")
    ok, _ = is_recent(item, max_age_days=35, reference_date=ref)
    assert ok is True


def test_item_outside_window_is_rejected():
    ref = datetime.date(2026, 10, 30)
    item = make_item(published_date="2026-09-01")
    ok, reason = is_recent(item, max_age_days=35, reference_date=ref)
    assert ok is False
    assert "excede la ventana" in reason


def test_item_without_published_date_is_rejected():
    item = make_item(published_date=None)
    ok, reason = is_recent(item, max_age_days=35)
    assert ok is False
    assert "sin published_date" in reason


def test_filter_recent_items_keeps_only_recent():
    ref = datetime.date(2026, 10, 30)
    items = [make_item("2026-10-25"), make_item("2026-01-01"), make_item(None)]
    kept = filter_recent_items(items, max_age_days=35, reference_date=ref)
    assert len(kept) == 1


def test_item_from_current_calendar_month_is_kept():
    ref = datetime.date(2026, 11, 18)
    item = make_item(published_date="2026-11-01")
    ok, _ = is_in_current_month(item, reference_date=ref)
    assert ok is True


def test_item_from_previous_month_is_rejected_even_if_within_35_days():
    # 2026-10-21 esta a 28 dias de 2026-11-18 (dentro de una ventana de 35 dias),
    # pero ya pertenece al mes calendario anterior: no debe repetirse en noviembre.
    ref = datetime.date(2026, 11, 18)
    item = make_item(published_date="2026-10-21")
    ok, reason = is_in_current_month(item, reference_date=ref)
    assert ok is False
    assert "fuera del mes en curso" in reason


def test_filter_items_in_current_month_keeps_only_this_month():
    ref = datetime.date(2026, 11, 18)
    items = [make_item("2026-11-05"), make_item("2026-10-30"), make_item("2026-12-01"), make_item(None)]
    kept = filter_items_in_current_month(items, reference_date=ref)
    assert len(kept) == 1
    assert kept[0].published_date == "2026-11-05"
