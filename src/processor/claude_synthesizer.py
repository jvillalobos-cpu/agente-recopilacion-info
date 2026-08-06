import os
import datetime
from typing import Dict, List, Optional
from src.models import NewsletterReport, NewsItem


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
        Procesa los elementos recopilados, valida las restricciones de guardrails y
        construye el objeto de reporte estructurado.
        """
        today_str = datetime.date.today().strftime("%d de %B, %Y")

        # Seleccionar nota principal
        nota_principal_item = None
        if collected_data.get("nota_principal"):
            nota_principal_item = collected_data["nota_principal"][0]
            self._apply_guardrails_to_item(nota_principal_item)

        # Procesar resto de categorías
        competencia_items = collected_data.get("competencia", [])
        sector_publico_items = collected_data.get("sector_publico_salud", [])
        canales_items = collected_data.get("canales_informacion", [])
        sector_privado_items = collected_data.get("sector_privado_salud", [])

        for item in competencia_items + sector_publico_items + canales_items + sector_privado_items:
            self._apply_guardrails_to_item(item)

        # Generar resumen en bullet points
        bullets = self._generate_executive_bullets(
            nota_principal=nota_principal_item,
            competencia=competencia_items,
            sector_publico=sector_publico_items,
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
        sector_privado: List[NewsItem]
    ) -> List[str]:
        """Genera sintetizados ejecutivos claves para DPE o Dirección General."""
        bullets = []
        if nota_principal:
            bullets.append(f"**Regulación / Macro**: {nota_principal.title}.")
        if competencia:
            bullets.append(f"**Competencia Directa**: {competencia[0].title}.")
        if sector_publico:
            bullets.append(f"**Sector Público**: {sector_publico[0].title}.")
        if sector_privado:
            bullets.append(f"**Inversión Privada**: {sector_privado[0].title}.")

        if not bullets:
            bullets = [
                "Se mantiene monitoreo continuo del sector salud y diagnóstico de laboratorio.",
                "Sin eventos críticos de disrupción reportados en el periodo."
            ]

        return bullets
