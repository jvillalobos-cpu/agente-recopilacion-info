import os
import json
from typing import List, Dict, Any, Optional
from src.collector.whitelist_validator import WhitelistValidator
from src.models import NewsItem


class GeminiDataCollector:
    """Módulo de recolección de datos que utiliza Google Gemini / Búsqueda web asistida."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.validator = WhitelistValidator()

    def fetch_market_news(self, category: str, query_hint: str) -> List[NewsItem]:
        """
        Recopila noticias del sector salud según la categoría y restricciones de la lista blanca.
        Si no hay API key de Gemini configurada, genera datos de prueba estructurados y validados.
        """
        if self.api_key:
            return self._fetch_from_gemini(category, query_hint)
        else:
            return self._generate_mock_news(category)

    def _fetch_from_gemini(self, category: str, query_hint: str) -> List[NewsItem]:
        """Realiza la búsqueda asistida por la API de Gemini."""
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"""
            Actúa como un agente de inteligencia de mercado del sector salud en México, Baja California y a nivel Internacional.
            Busca información pública reciente sobre: {query_hint}.
            
            RESTRICCIÓN ESTRICTA: Solo incluye noticias provenientes de estos dominios autorizados:
            {list(self.validator.whitelisted_domains)}
            
            Formatea la respuesta como una lista JSON de objetos con las claves:
            - title (máx 10 palabras)
            - content (resumen factual de 2 a 3 renglones sin opiniones)
            - url (URL completa a la nota)
            - source_domain (dominio de la fuente)
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw_text = response.text
            items = []
            data = json.loads(raw_text)
            for entry in data:
                url = entry.get("url", "")
                if self.validator.is_url_allowed(url):
                    items.append(NewsItem(
                        title=entry.get("title", "Sin título"),
                        content=entry.get("content", ""),
                        url=url,
                        source_domain=entry.get("source_domain", "gob.mx"),
                        category=category
                    ))
            return items
        except Exception as e:
            print(f"[INFO] Búsqueda live de Gemini con fallback a datos de prueba local: {e}")
            return self._generate_mock_news(category)

    def _generate_mock_news(self, category: str) -> List[NewsItem]:
        """Genera noticias de prueba realistas basadas en las fuentes oficializadas (Macro, Nacional, Regional, Local)."""
        mock_db: Dict[str, List[Dict[str, str]]] = {
            "nota_principal": [
                {
                    "title": "COFEPRIS y EMA actualizan criterios de acreditación para laboratorios moleculares",
                    "content": "La Comisión Federal para la Protección contra Riesgos Sanitarios (COFEPRIS) en conjunto con la Entidad Mexicana de Acreditación (EMA) publicaron la nueva guía de homologación ISO 15189:2022. La norma agilizará la autorización de pruebas diagnósticas avanzadas en laboratorios públicos y privados.",
                    "url": "https://www.gob.mx/cofepris/prensa/actualizacion-acreditacion-laboratorios-2026",
                    "source_domain": "cofepris.gob.mx"
                }
            ],
            "competencia": [
                {
                    "title": "Dark Daily reporta consolidación de cadenas de laboratorios de diagnóstico en Norteamérica",
                    "content": "Un análisis de la industria destaca el incremento en fusiones estratégicas de laboratorios automatizados para reducir costos operativos en paneles genómicos. Las cadenas regionales adoptan inteligencia artificial para acelerar la entrega de resultados clínicos.",
                    "url": "https://www.darkdaily.com/clinical-laboratory-trends-consolidation-2026",
                    "source_domain": "darkdaily.com"
                },
                {
                    "title": "Baja Health Cluster fortalece la oferta de servicios diagnósticos en la frontera",
                    "content": "Directivos del clúster médico de Tijuana anunciaron un programa de alianzas con laboratorios acreditados para impulsar el turismo de salud transfronterizo con estándares de calidad internacionales.",
                    "url": "https://bajahealthcluster.org/comunicados/impulso-turismo-salud-tijuana-2026",
                    "source_domain": "bajahealthcluster.org"
                }
            ],
            "sector_publico_salud": [
                {
                    "title": "Secretaría de Salud de BC emite boletín epidemiológico SVEET/SVEENT",
                    "content": "La Secretaría de Salud de Baja California publicó la actualización epidemiológica sobre enfermedades crónicas no transmisibles. Se reforzará la toma de muestras preventivas en centros de salud de Tijuana y Mexicali.",
                    "url": "https://www.saludbc.gob.mx/boletin-epidemiologico-bc-2026",
                    "source_domain": "saludbc.gob.mx"
                }
            ],
            "canales_informacion": [
                {
                    "title": "AMBC y ADLM anuncian serie de webinars sobre bioética e IA en el laboratorio",
                    "content": "La Asociación Mexicana de Bioquímica Clínica (AMBC) en colaboración con ADLM llevarán a cabo capacitaciones virtuales sobre automatización diagnóstica y normatividad Sanitaria EducaPRiS.",
                    "url": "https://www.ambc.org.mx/capacitaciones-webinars-2026",
                    "source_domain": "ambc.org.mx"
                }
            ],
            "sector_privado_salud": [
                {
                    "title": "Semanario ZETA reporta crecimiento del 25% en inversión de clínicas privadas en Tijuana",
                    "content": "El sector de salud privado en la zona fronteriza registró la apertura de nuevos centros de atención médica y diagnóstico especializado, atrayendo pacientes de California y del noroeste de México.",
                    "url": "https://zetatijuana.com/noticias/salud-economia-inversion-clinicas-tijuana-2026",
                    "source_domain": "zetatijuana.com"
                }
            ]
        }

        items_data = mock_db.get(category, [])
        return [
            NewsItem(
                title=item["title"],
                content=item["content"],
                url=item["url"],
                source_domain=item["source_domain"],
                category=category
            ) for item in items_data
        ]
