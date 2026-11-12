import re
import datetime
from typing import List, Optional
from src.models import NewsItem
from src.processor.claude_synthesizer import format_date_es, MESES_ES

PRESIDENCIA_ARCHIVE_URL = "https://www.gob.mx/presidencia/es/archivo/articulos?idiom=es"

# Palabras clave que delimitan el bloque de salud dentro de la version estenografica completa.
HEALTH_KEYWORDS = [
    "imss-bienestar", "imss", "isste", "cofepris", "secretaría de salud",
    "secretaria de salud", "salud pública", "salud publica",
]


class MananeraSaludCollector:
    """
    Recolector del bloque de salud (IMSS / ISSSTE / IMSS-Bienestar / COFEPRIS) que la
    Presidencia de la República suele dedicar los martes dentro de la conferencia de
    prensa matutina ("mañanera").

    Fuente: la versión estenográfica oficial publicada en gob.mx/presidencia (dominio ya
    autorizado en la lista blanca vía el match de subdominio de "gob.mx"). No es scraping
    de redes sociales ni de video: se trata de un documento de texto publicado oficialmente
    por la Presidencia.

    Si no hay acceso de red al sitio oficial (p. ej. en este entorno de desarrollo, sin
    resolución DNS a gob.mx), se retornan datos de prueba marcados [MOCK] para no bloquear
    el resto del pipeline -- igual que CLUESCollector.
    """

    def __init__(self, archive_url: str = PRESIDENCIA_ARCHIVE_URL):
        self.archive_url = archive_url

    def fetch_latest_tuesday_health_block(self, reference_date: Optional[datetime.date] = None) -> List[NewsItem]:
        """
        Ubica la versión estenográfica del martes más reciente (hoy mismo si hoy es
        martes) y, si el texto contiene el bloque de salud, retorna una NewsItem con el
        resumen. Si no se puede acceder a la fuente oficial, retorna datos de prueba.
        """
        tuesday = self._most_recent_tuesday(reference_date or datetime.date.today())
        try:
            transcript_url, raw_text = self._fetch_transcript_for_date(tuesday)
        except Exception as e:
            print(f"[INFO] No se pudo acceder a la versión estenográfica de Presidencia, usando datos de prueba: {e}")
            return self._generate_mock_items(tuesday)

        excerpt = self._extract_health_excerpt(raw_text)
        if not excerpt:
            # El documento existe pero no trae bloque de salud reconocible ese día.
            return []

        return [NewsItem(
            title=f"Bloque de salud en la mañanera del {format_date_es(tuesday)}",
            content=excerpt,
            url=transcript_url,
            source_domain="gob.mx",
            category="sector_publico_salud",
            published_date=tuesday.isoformat()
        )]

    def _most_recent_tuesday(self, reference_date: datetime.date) -> datetime.date:
        """Martes de la semana en curso: hoy mismo si es martes, si no el martes previo."""
        days_since_tuesday = (reference_date.weekday() - 1) % 7
        return reference_date - datetime.timedelta(days=days_since_tuesday)

    def _fetch_transcript_for_date(self, target_date: datetime.date) -> (str, str):
        """
        Busca en el archivo de Presidencia la versión estenográfica del día indicado y
        retorna (url, texto_completo). Lanza excepción si no hay acceso de red o no se
        encuentra la publicación de esa fecha.
        """
        import requests

        mes_es = MESES_ES[target_date.month - 1]
        search_url = (
            f"https://www.gob.mx/presidencia/es/archivo/articulos"
            f"?idiom=es&q=versi%C3%B3n+estenogr%C3%A1fica+{target_date.day:02d}+de+{mes_es}+de+{target_date.year}"
        )
        response = requests.get(search_url, timeout=30)
        response.raise_for_status()
        html = response.text

        match = re.search(r'href="(/presidencia/[^"]*version-estenografica[^"]*)"', html, re.IGNORECASE)
        if not match:
            raise ValueError(f"No se encontró versión estenográfica para {target_date.isoformat()} en el archivo oficial.")

        transcript_url = "https://www.gob.mx" + match.group(1)
        transcript_response = requests.get(transcript_url, timeout=30)
        transcript_response.raise_for_status()
        return transcript_url, transcript_response.text

    def _extract_health_excerpt(self, raw_text: str, max_chars: int = 1200) -> Optional[str]:
        """Extrae un fragmento del texto alrededor de la primera mención fuerte de salud."""
        plain = re.sub(r"<[^>]+>", " ", raw_text)
        plain = re.sub(r"\s+", " ", plain).strip()
        lower = plain.lower()

        for keyword in HEALTH_KEYWORDS:
            idx = lower.find(keyword)
            if idx != -1:
                start = max(0, idx - 200)
                end = min(len(plain), idx + max_chars)
                return plain[start:end].strip()
        return None

    def _generate_mock_items(self, tuesday: datetime.date) -> List[NewsItem]:
        """Dato de referencia para dry-run sin acceso de red al sitio oficial de Presidencia."""
        return [NewsItem(
            title=f"[MOCK] Bloque de salud en la mañanera del {format_date_es(tuesday)}",
            content=(
                "Dato de referencia generado en modo de prueba porque no hay acceso de red a "
                "gob.mx/presidencia en este entorno. En producción se listaría aquí el resumen real "
                "del bloque de salud (IMSS, ISSSTE, IMSS-Bienestar, COFEPRIS) de la versión "
                "estenográfica oficial del martes correspondiente."
            ),
            url=PRESIDENCIA_ARCHIVE_URL,
            source_domain="gob.mx",
            category="sector_publico_salud",
            published_date=tuesday.isoformat()
        )]
