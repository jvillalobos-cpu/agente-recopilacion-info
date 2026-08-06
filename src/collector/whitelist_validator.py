import json
from urllib.parse import urlparse
from typing import List, Set


class WhitelistValidator:
    """Validador estricto para asegurar que solo se procesen fuentes permitidas."""

    def __init__(self, sources_file_path: str = "config/sources.json"):
        self.sources_file_path = sources_file_path
        self.whitelisted_domains: Set[str] = set()
        self.load_sources()

    def load_sources(self):
        """Carga los dominios autorizados desde el archivo de configuración."""
        try:
            with open(self.sources_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.whitelisted_domains = set(data.get("whitelisted_domains", []))
        except Exception as e:
            print(f"[WARN] Error cargando lista blanca de fuentes ({e}). Usando valores por defecto.")
            self.whitelisted_domains = {
                "gob.mx", "cofepris.gob.mx", "imss.gob.mx", "who.int", "paho.org",
                "elfinanciero.com.mx", "eleconomista.com.mx", "expansion.mx"
            }

    def is_url_allowed(self, url: str) -> bool:
        """Verifica si el dominio de la URL proporcionada está en la lista blanca."""
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            for allowed in self.whitelisted_domains:
                if domain == allowed or domain.endswith("." + allowed):
                    return True
            return False
        except Exception:
            return False

    def filter_urls(self, urls: List[str]) -> List[str]:
        """Filtra una lista de URLs retornando únicamente las permitidas."""
        return [url for url in urls if self.is_url_allowed(url)]
