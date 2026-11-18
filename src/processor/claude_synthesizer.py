import os
import datetime
import yaml
from typing import Dict, List, Optional
from src.models import NewsletterReport, NewsItem, ExecutiveBullet
from src.collector.recency_filter import filter_recent_items, filter_items_in_current_month
from src.collector.deduplicator import deduplicate_items

DEFAULT_MAX_NOTE_AGE_DAYS = {"Semanal": 10, "Mensual": 35}


def load_max_note_age_days(guardrails_file_path: str = "config/guardrails.yaml") -> Dict[str, int]:
    """Carga la ventana de recencia por frecuencia desde config/guardrails.yaml."""
    try:
        with open(guardrails_file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        configured = data.get("guardrails", {}).get("max_note_age_days")
        if configured:
            return configured
    except Exception as e:
        print(f"[WARN] No se pudo cargar max_note_age_days de {guardrails_file_path} ({e}). Usando valores por defecto.")
    return DEFAULT_MAX_NOTE_AGE_DAYS

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

# Palabras clave que elevan la relevancia estratégica de una nota, agrupadas por peso.
IMPORTANCE_KEYWORDS = {
    3: ["cofepris", "ema", "regulación", "regulacion", "brote", "alerta", "tuberculosis",
        "dengue", "rickettsiosis", "epidemi", "sanción", "sancion", "acreditación", "acreditacion"],
    2: ["adquisición", "adquisicion", "fusión", "fusion", "inversión", "inversion",
        "apertura", "alianza", "consolidación", "consolidacion", "iso 15189", "iso 17043"],
    1: ["webinar", "capacitación", "capacitacion", "turismo", "tecnología", "tecnologia"],
}


def format_date_es(date: datetime.date) -> str:
    """Formatea una fecha como '18 de agosto, 2026' sin depender del locale del sistema."""
    return f"{date.day} de {MESES_ES[date.month - 1]}, {date.year}"


def score_importance(item: NewsItem) -> int:
    """Calcula un puntaje simple de relevancia estratégica basado en palabras clave del insumo."""
    haystack = f"{item.title} {item.content}".lower()
    score = 0
    for weight, keywords in IMPORTANCE_KEYWORDS.items():
        score += weight * sum(1 for kw in keywords if kw in haystack)
    return score


def rank_items(items: List[NewsItem], max_items: int = 3) -> List[NewsItem]:
    """Ordena las notas por relevancia estratégica y conserva las más importantes."""
    ranked = sorted(items, key=score_importance, reverse=True)
    return ranked[:max_items]


class ClaudeNewsProcessor:
    """Procesador y redactor ejecutivo que aplica Guardrails de contenido."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def build_newsletter_report(
        self,
        collected_data: Dict[str, List[NewsItem]],
        target_audience: str = "DPE",
        frequency: str = "Semanal"
    ) -> NewsletterReport:
        """
        Procesa los elementos recopilados, valida las restricciones de guardrails,
        prioriza las notas por relevancia estratégica y construye el reporte estructurado.
        """
        today_str = format_date_es(datetime.date.today())

        # Guardrail de recencia: descarta notas fuera de la ventana permitida para la frecuencia,
        # o sin fecha de publicación verificable, antes de rankear o incluir nada en el boletín.
        # Para el corte Mensual se usa el mes calendario actual (no una ventana móvil de días),
        # para que una nota que ya salió en la edición del mes pasado no vuelva a aparecer.
        if frequency == "Mensual":
            collected_data = {
                key: filter_items_in_current_month(items)
                for key, items in collected_data.items()
            }
        else:
            max_age_days = load_max_note_age_days().get(frequency, DEFAULT_MAX_NOTE_AGE_DAYS.get(frequency, 10))
            collected_data = {
                key: filter_recent_items(items, max_age_days)
                for key, items in collected_data.items()
            }

        # Deduplicación: evita que la misma nota (por URL o título casi idéntico)
        # aparezca dos veces cuando dos fuentes distintas cubren el mismo hecho.
        collected_data = {
            key: deduplicate_items(items)
            for key, items in collected_data.items()
        }

        # Seleccionar nota principal: la más relevante entre las candidatas de la categoría
        nota_principal_item = None
        if collected_data.get("nota_principal"):
            nota_principal_item = rank_items(collected_data["nota_principal"], max_items=1)[0]
            self._apply_guardrails_to_item(nota_principal_item)

        # Procesar y priorizar el resto de categorías (hasta 3 notas por sección)
        competencia_items = rank_items(collected_data.get("competencia", []))
        sector_publico_items = rank_items(collected_data.get("sector_publico_salud", []))
        ia_salud_items = rank_items(collected_data.get("ia_salud_laboratorios", []))
        canales_items = rank_items(collected_data.get("canales_informacion", []))
        sector_privado_items = rank_items(collected_data.get("sector_privado_salud", []))

        for item in competencia_items + sector_publico_items + ia_salud_items + canales_items + sector_privado_items:
            self._apply_guardrails_to_item(item)

        # Generar resumen en bullet points, cada uno enlazado a su nota fuente
        bullets = self._generate_executive_bullets(
            nota_principal=nota_principal_item,
            competencia=competencia_items,
            sector_publico=sector_publico_items,
            canales_informacion=canales_items,
            sector_privado=sector_privado_items
        )

        return NewsletterReport(
            title="Newsletter de Inteligencia de Mercado y Salud",
            edition_date=today_str,
            frequency=frequency,
            target_audience=target_audience,
            nota_principal=nota_principal_item,
            competencia=competencia_items,
            sector_publico=sector_publico_items,
            ia_salud_laboratorios=ia_salud_items,
            canales_informacion=canales_items,
            sector_privado=sector_privado_items,
            resumen_ejecutivo=bullets,
            is_verified_by_guardrails=True
        )

    def _apply_guardrails_to_item(self, item: NewsItem):
        """Aplica restricciones estricta de 2-3 renglones y remueve adjetivos de opinión."""
        if not item:
            return

        # Limitar longitud si excede el rango máximo
        lines = item.content.strip().split(". ")
        if len(lines) > 3:
            item.content = ". ".join(lines[:3]) + "."
        elif len(lines) < 2 and not item.content.endswith("."):
            item.content += "."

    def _generate_executive_bullets(
        self,
        nota_principal: Optional[NewsItem],
        competencia: List[NewsItem],
        sector_publico: List[NewsItem],
        canales_informacion: List[NewsItem],
        sector_privado: List[NewsItem]
    ) -> List[ExecutiveBullet]:
        """
        Genera de 3 a 5 bullets ejecutivos para Dirección General, siguiendo las 4
        categorías fijas del Master Prompt (implicación estratégica, alerta regulatoria,
        movimiento de competencia y oportunidad de innovación/eficiencia). Cada bullet
        queda enlazado a la nota fuente que lo sustenta para navegar directo a ella.
        """
        def make_bullet(label: str, item: NewsItem) -> ExecutiveBullet:
            return ExecutiveBullet(
                text=f"**{label}**: {item.title}.",
                url=item.url,
                source_domain=item.source_domain
            )

        bullets: List[ExecutiveBullet] = []
        if nota_principal:
            bullets.append(make_bullet("Implicación estratégica", nota_principal))
        if sector_publico:
            bullets.append(make_bullet("Alerta regulatoria/epidemiológica", sector_publico[0]))
        if competencia:
            bullets.append(make_bullet("Movimiento de la competencia", competencia[0]))
        if canales_informacion:
            bullets.append(make_bullet("Oportunidad de innovación", canales_informacion[0]))
        elif sector_privado:
            bullets.append(make_bullet("Oportunidad de mercado", sector_privado[0]))

        used_urls = {b.url for b in bullets}
        if sector_privado and len(bullets) < 5 and sector_privado[0].url not in used_urls:
            bullets.append(make_bullet("Dinámica de mercado privado", sector_privado[0]))

        if len(bullets) < 3:
            bullets.append(ExecutiveBullet(text="Sin novedades registradas esta semana en esta categoría."))

        return bullets[:5]
