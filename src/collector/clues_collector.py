import os
import json
import datetime
from io import BytesIO
from typing import List, Optional, Dict, Any
from src.models import NewsItem

CLUES_CATALOG_URL = "http://www.dgis.salud.gob.mx/descargas/clues/CLUES_Agosto2026.xlsx"
CLUES_CATALOG_PAGE = "https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-informacion-en-salud-dgis"
DEFAULT_SNAPSHOT_PATH = "data/clues_snapshot_baja_california.json"

# Instituciones/tipos que nos interesan: establecimientos PRIVADOS de diagnóstico/laboratorio.
LAB_KEYWORDS = ["laboratorio", "análisis clínico", "analisis clinico", "diagnóstico", "diagnostico"]
TARGET_MUNICIPIOS = ["tijuana", "rosarito", "playas de rosarito", "ensenada", "mexicali", "tecate"]


class CLUESCollector:
    """
    Recolector sobre el catálogo CLUES (Clave Única de Establecimientos de Salud) que
    administra la Dirección General de Información en Salud (DGIS, gob.mx). Es el
    directorio oficial nacional de establecimientos de salud en México -- de uso
    obligatorio para el Sistema Nacional de Salud según acuerdo del DOF -- e incluye
    laboratorios y clínicas privadas con su ubicación, institución y estatus.

    No es scraping: se descarga el catálogo oficial publicado por la DGIS y se compara
    contra la última instantánea (snapshot) guardada localmente para detectar altas
    (nuevos registros) y bajas de establecimientos privados de diagnóstico en Baja
    California, como señal sistemática de movimientos de competencia -- en vez de
    depender de hallazgos manuales (ej. fichas de Google Business).
    """

    def __init__(
        self,
        catalog_url: str = CLUES_CATALOG_URL,
        snapshot_path: str = DEFAULT_SNAPSHOT_PATH,
    ):
        self.catalog_url = catalog_url
        self.snapshot_path = snapshot_path

    def fetch_new_competitor_registrations(self) -> List[NewsItem]:
        """
        Descarga el catálogo CLUES, filtra a laboratorios/diagnóstico privados en BC,
        compara contra el snapshot anterior y retorna una NewsItem por cada
        establecimiento nuevo detectado. Si no se puede descargar el catálogo (sin
        acceso de red, por ejemplo en desarrollo), retorna datos de prueba.
        """
        try:
            current = self._download_and_filter()
        except Exception as e:
            print(f"[INFO] No se pudo descargar el catálogo CLUES, usando datos de prueba: {e}")
            return self._generate_mock_items()

        previous = self._load_snapshot()
        previous_ids = {row["clues_id"] for row in previous}

        new_rows = [row for row in current if row["clues_id"] not in previous_ids]

        self._save_snapshot(current)

        today = datetime.date.today().isoformat()
        items = []
        for row in new_rows:
            items.append(NewsItem(
                title=f"Nuevo registro en CLUES: {row['nombre']} ({row['municipio']})",
                content=(
                    f"El catálogo oficial CLUES (DGIS) registra un nuevo establecimiento privado "
                    f"de diagnóstico en {row['municipio']}, Baja California: {row['nombre']}, "
                    f"tipo {row['tipo']}. Detectado por comparación de catálogo, no por cobertura "
                    f"de prensa -- se recomienda verificar directamente antes de asumir fecha de apertura exacta."
                ),
                url=CLUES_CATALOG_PAGE,
                source_domain="gob.mx",
                category="competencia",
                published_date=today
            ))
        return items

    def _download_and_filter(self) -> List[Dict[str, Any]]:
        import requests
        import pandas as pd

        response = requests.get(self.catalog_url, timeout=60)
        response.raise_for_status()

        df = pd.read_excel(BytesIO(response.content))
        df.columns = [str(c).strip().upper() for c in df.columns]

        rows: List[Dict[str, Any]] = []
        for _, r in df.iterrows():
            municipio = str(r.get("MUNICIPIO", "")).strip().lower()
            institucion = str(r.get("INSTITUCION", "")).strip().lower()
            tipo = str(r.get("TIPO ESTABLECIMIENTO", r.get("TIPOLOGIA", ""))).strip()
            nombre = str(r.get("NOMBRE DE LA UNIDAD", r.get("NOMBRE", ""))).strip()
            clues_id = str(r.get("CLUES", "")).strip()

            if municipio not in TARGET_MUNICIPIOS:
                continue
            if "privad" not in institucion:
                continue
            if not any(kw in tipo.lower() or kw in nombre.lower() for kw in LAB_KEYWORDS):
                continue
            if not clues_id:
                continue

            rows.append({
                "clues_id": clues_id,
                "nombre": nombre,
                "tipo": tipo,
                "municipio": municipio.title(),
            })
        return rows

    def _load_snapshot(self) -> List[Dict[str, Any]]:
        try:
            with open(self.snapshot_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_snapshot(self, rows: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self.snapshot_path), exist_ok=True)
        with open(self.snapshot_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    def _generate_mock_items(self) -> List[NewsItem]:
        """Datos de prueba estructurados para dry-run sin acceso de red al catálogo real."""
        return [
            NewsItem(
                title="[MOCK] Nuevo registro en CLUES: Laboratorio de prueba (Tijuana)",
                content=(
                    "Dato de referencia generado en modo de prueba porque no hay acceso de red al "
                    "catálogo CLUES de la DGIS en este entorno. En producción se listarían aquí los "
                    "establecimientos privados de diagnóstico realmente detectados como altas nuevas "
                    "en Baja California."
                ),
                url=CLUES_CATALOG_PAGE,
                source_domain="gob.mx",
                category="competencia",
                published_date=datetime.date.today().isoformat()
            )
        ]
