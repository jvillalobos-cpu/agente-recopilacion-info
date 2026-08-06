import os
from src.collector.gemini_search import GeminiDataCollector
from src.processor.claude_synthesizer import ClaudeNewsProcessor
from src.newsletter.renderer import NewsletterRenderer


def test_newsletter_generation_flow():
    collector = GeminiDataCollector()
    data = {
        "nota_principal": collector.fetch_market_news("nota_principal", "salud"),
        "competencia": collector.fetch_market_news("competencia", "laboratorio"),
        "sector_publico_salud": collector.fetch_market_news("sector_publico_salud", "imss"),
        "canales_informacion": collector.fetch_market_news("canales_informacion", "redes"),
        "sector_privado_salud": collector.fetch_market_news("sector_privado_salud", "privado")
    }
    
    processor = ClaudeNewsProcessor()
    report = processor.build_newsletter_report(data, target_audience="DPE", frequency="Semanal")
    
    assert report.title == "Newsletter de Inteligencia de Mercado y Salud"
    assert report.is_verified_by_guardrails == True
    assert report.nota_principal is not None
    assert len(report.resumen_ejecutivo) > 0

    renderer = NewsletterRenderer()
    html_output = renderer.render_html(report)
    assert "Inteligencia de Mercado" in html_output
    assert report.nota_principal.title in html_output
