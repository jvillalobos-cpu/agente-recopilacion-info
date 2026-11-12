from src.collector.clues_collector import CLUESCollector


def test_falls_back_to_mock_without_network():
    collector = CLUESCollector(catalog_url="http://invalid.local/no-existe.xlsx")
    items = collector.fetch_new_competitor_registrations()
    assert len(items) == 1
    assert items[0].title.startswith("[MOCK]")
    assert items[0].category == "competencia"
    assert items[0].source_domain == "gob.mx"


def test_detects_new_registration_against_snapshot(tmp_path, monkeypatch):
    snapshot_path = tmp_path / "snapshot.json"
    collector = CLUESCollector(snapshot_path=str(snapshot_path))

    def fake_download_and_filter():
        return [{"clues_id": "BC000123", "nombre": "Laboratorio Nuevo", "tipo": "Laboratorio", "municipio": "Tijuana"}]

    monkeypatch.setattr(collector, "_download_and_filter", fake_download_and_filter)
    items = collector.fetch_new_competitor_registrations()
    assert len(items) == 1
    assert "Laboratorio Nuevo" in items[0].title

    # Segunda corrida: ya está en el snapshot, no debe reportarse de nuevo.
    items_again = collector.fetch_new_competitor_registrations()
    assert len(items_again) == 0
