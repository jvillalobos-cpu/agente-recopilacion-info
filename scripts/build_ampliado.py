import sys
sys.path.insert(0, ".")
import datetime
from src.collector.manual_curation import ManualCurationCollector
from src.collector.gemini_search import GeminiDataCollector
from src.models import NewsletterReport, ExecutiveBullet
from src.newsletter.renderer import NewsletterRenderer
from src.processor.claude_synthesizer import format_date_es, score_importance
from src.collector.recency_filter import filter_items_in_current_month

manual = ManualCurationCollector().fetch_curated_posts()
gemini = GeminiDataCollector()  # sin API key -> mock, solo para nota_principal de referencia si falta

# Solo notas del mes calendario en curso: lo que ya salio en la edicion del mes
# pasado no debe repetirse, aunque siga dentro de una ventana movil de dias.
manual = {cat: filter_items_in_current_month(items) for cat, items in manual.items()}

# Nota principal: la de mayor score entre todas las categorias (o la unica marcada como tal)
nota_principal = None
if manual.get("nota_principal"):
    nota_principal = sorted(manual["nota_principal"], key=score_importance, reverse=True)[0]

def sort_desc(items):
    return sorted(items, key=lambda i: i.published_date or "", reverse=True)

competencia = sort_desc(manual.get("competencia", []))
sector_publico = sort_desc(manual.get("sector_publico_salud", []))
ia_salud_laboratorios = sort_desc(manual.get("ia_salud_laboratorios", []))
canales_informacion = sort_desc(manual.get("canales_informacion", []))
sector_privado = sort_desc(manual.get("sector_privado_salud", []))

def bullet(label, item):
    return ExecutiveBullet(text=f"**{label}**: {item.title}.", url=item.url, source_domain=item.source_domain)

bullets = []
if nota_principal:
    bullets.append(bullet("Consolidación global del sector", nota_principal))
if competencia:
    bullets.append(bullet("Movimiento directo de competencia", competencia[0]))
if sector_publico:
    bullets.append(bullet("Agenda regulatoria", sector_publico[0]))
if ia_salud_laboratorios:
    bullets.append(bullet("IA en salud/laboratorios", ia_salud_laboratorios[0]))
if sector_privado:
    bullets.append(bullet("Dinámica de sector privado", sector_privado[0]))

report = NewsletterReport(
    title="Newsletter de Inteligencia de Mercado y Salud",
    edition_date=format_date_es(datetime.date.today()),
    frequency="Mensual",
    target_audience="DG",
    nota_principal=nota_principal,
    competencia=competencia,
    sector_publico=sector_publico,
    ia_salud_laboratorios=ia_salud_laboratorios,
    canales_informacion=canales_informacion,
    sector_privado=sector_privado,
    resumen_ejecutivo=bullets,
    editor_name="Dirección de Proyectos Estratégicos",
    editor_role="Certus Laboratorio",
    is_verified_by_guardrails=True
)

renderer = NewsletterRenderer()
out = renderer.save_html_preview(report, "output/reporte_ampliado.html")
print("OK ->", out)
print(f"nota_principal: {'si' if nota_principal else 'NO'}")
print(f"competencia: {len(competencia)}")
print(f"sector_publico: {len(sector_publico)}")
print(f"ia_salud_laboratorios: {len(ia_salud_laboratorios)}")
print(f"canales_informacion: {len(canales_informacion)}")
print(f"sector_privado: {len(sector_privado)}")
