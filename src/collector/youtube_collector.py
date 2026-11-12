import os
import json
import datetime
from typing import List, Dict, Any, Optional
from src.models import NewsItem

DEFAULT_SOURCES_PATH = "config/sources.json"


class YouTubeCollector:
    """
    Recolector de videos recientes de canales oficiales de YouTube, basado en la
    YouTube Data API v3 (sin scraping de HTML). Revisa únicamente los canales
    configurados en config/sources.json bajo "canales_youtube_oficiales"
    (ej. COFEPRIS, ADLM, Baja Health Cluster).
    """

    def __init__(self, api_key: Optional[str] = None, sources_path: str = DEFAULT_SOURCES_PATH):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.sources_path = sources_path
        self.channels = self._load_channels()

    def _load_channels(self) -> List[Dict[str, str]]:
        try:
            with open(self.sources_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("canales_youtube_oficiales", [])
        except Exception as e:
            print(f"[WARN] No se pudieron cargar canales_youtube_oficiales de {self.sources_path}: {e}")
            return []

    def fetch_recent_videos(self, days: int = 7) -> List[NewsItem]:
        """
        Retorna videos publicados en los últimos `days` días en los canales oficiales
        configurados. Si no hay API key de YouTube, retorna datos de prueba marcados [MOCK]
        para no bloquear el resto del pipeline.
        """
        if not self.api_key or not self.channels:
            return self._generate_mock_items()

        try:
            return self._fetch_from_api(days)
        except Exception as e:
            print(f"[INFO] No se pudo consultar la YouTube Data API, usando datos de prueba: {e}")
            return self._generate_mock_items()

    def _fetch_from_api(self, days: int) -> List[NewsItem]:
        import requests

        published_after = (
            datetime.datetime.utcnow() - datetime.timedelta(days=days)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        items: List[NewsItem] = []
        for channel in self.channels:
            channel_id = channel.get("channel_id")
            channel_name = channel.get("name", channel_id)
            if not channel_id:
                continue

            response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "key": self.api_key,
                    "channelId": channel_id,
                    "part": "snippet",
                    "order": "date",
                    "type": "video",
                    "publishedAfter": published_after,
                    "maxResults": 5,
                },
                timeout=30,
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            for video in data.get("items", []):
                snippet = video.get("snippet", {})
                video_id = video.get("id", {}).get("videoId")
                if not video_id:
                    continue
                items.append(NewsItem(
                    title=f"{channel_name}: {snippet.get('title', 'Video sin título')}",
                    content=snippet.get("description", "")[:300] or "Sin descripción disponible.",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    source_domain="youtube.com",
                    category="canales_informacion",
                    published_date=(snippet.get("publishedAt", "")[:10] or None),
                ))
        return items

    def _generate_mock_items(self) -> List[NewsItem]:
        """Dato de referencia para dry-run sin API key de YouTube configurada."""
        return [NewsItem(
            title="[MOCK] Canal oficial: video reciente de referencia",
            content=(
                "Dato de referencia generado en modo de prueba porque no hay YOUTUBE_API_KEY "
                "configurada en este entorno. En producción se listarían aquí los videos "
                "recientes de los canales oficiales configurados en config/sources.json."
            ),
            url="https://www.youtube.com/",
            source_domain="youtube.com",
            category="canales_informacion",
            published_date=datetime.date.today().isoformat()
        )]
