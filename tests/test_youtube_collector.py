from src.collector.youtube_collector import YouTubeCollector


def test_falls_back_to_mock_without_api_key():
    collector = YouTubeCollector(api_key=None)
    items = collector.fetch_recent_videos()
    assert len(items) == 1
    assert items[0].title.startswith("[MOCK]")
    assert items[0].category == "canales_informacion"
    assert items[0].source_domain == "youtube.com"


def test_loads_channels_from_sources_json():
    collector = YouTubeCollector(api_key=None)
    names = [c.get("name") for c in collector.channels]
    assert "COFEPRIS" in names
