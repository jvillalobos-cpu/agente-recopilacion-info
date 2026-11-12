import os
import sys
import argparse
from dotenv import load_dotenv
from src.collector.config_validator import print_validation_report
from src.collector.gemini_search import GeminiDataCollector
from src.collector.youtube_collector import YouTubeCollector
from src.collector.manual_curation import ManualCurationCollector
from src.collector.clues_collector import CLUESCollector
from src.collector.mananera_collector import MananeraSaludCollector
from src.processor.claude_synthesizer import ClaudeNewsProcessor
from src.newsletter.renderer import NewsletterRenderer
from src.delivery.resend_mailer import ResendEmailDelivery

# Cargar variables de entorno
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Agente de Inteligencia de Mercado y Sector Salud"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Genera el newsletter localmente en HTML sin realizar envíos de correo."
    )
    parser.add_argument(
        "--audience",
        type=str,
        default="DPE",
        choices=["DPE", "Departamentos", "DG"],
        help="Audiencia objetivo del reporte (DPE, Departamentos o Dirección General)."
    )
    parser.add_argument(
        "--frequency",
        type=str,
        default="Semanal",
        choices=["Semanal", "Mensual"],
        help="Frecuencia de edición del boletín."
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Envía el correo vía Resend a los destinatarios configurados."
    )
    args = parser.parse_args()

    print("==========================================================")
    print(" [AGENTE DE INTELIGENCIA DE MERCADO Y SECTOR SALUD]")
    print("==========================================================")
    print(f"Audiencia: {args.audience} | Frecuencia: {args.frequency}")

    # 0. Validación de configuración: la lista blanca es la base de todos los guardrails.
    if not print_validation_report():
        print("[ERROR] config/sources.json tiene errores críticos. Abortando ejecución.")
        sys.exit(1)

    print("Iniciando recoleccion de noticias y analisis de mercado...")

    # 1. Recolección de noticias asistida por Gemini
    collector = GeminiDataCollector()
    collected_data = {
        "nota_principal": collector.fetch_market_news("nota_principal", "noticia principal mercado salud laboratorio mexico"),
        "competencia": collector.fetch_market_news("competencia", "competencia laboratorios clinicos diagnostico mexico"),
        "sector_publico_salud": collector.fetch_market_news("sector_publico_salud", "sector publico salud cofepris imss licitaciones"),
        "canales_informacion": collector.fetch_market_news("canales_informacion", "divulgacion medica redes sociales youtube salud"),
        "sector_privado_salud": collector.fetch_market_news("sector_privado_salud", "sector privado salud hospitales inversion laboratorio"),
        "ia_salud_laboratorios": collector.fetch_market_news("ia_salud_laboratorios", "inteligencia artificial diagnostico laboratorio clinico salud")
    }

    # 1b. Recolección de videos recientes de canales oficiales de YouTube (API oficial, sin scraping)
    youtube_collector = YouTubeCollector()
    collected_data["canales_informacion"].extend(youtube_collector.fetch_recent_videos(days=7))

    # 1c. Posts curados a mano (Instagram, X, LinkedIn) de personas/empresas sin blog propio
    manual_collector = ManualCurationCollector()
    manual_posts = manual_collector.fetch_curated_posts()
    for category, items in manual_posts.items():
        collected_data.setdefault(category, []).extend(items)

    # 1d. Nuevos registros de laboratorios/clínicas privadas en BC vía catálogo oficial CLUES (DGIS)
    clues_collector = CLUESCollector()
    collected_data["competencia"].extend(clues_collector.fetch_new_competitor_registrations())

    # 1e. Bloque de salud de la mañanera presidencial (habitualmente los martes)
    mananera_collector = MananeraSaludCollector()
    collected_data["sector_publico_salud"].extend(mananera_collector.fetch_latest_tuesday_health_block())

    print("[OK] Noticias recopiladas y filtradas mediante Lista Blanca (Guardrails).")

    # 2. Procesamiento y síntesis con Claude / Guardrails
    processor = ClaudeNewsProcessor()
    report = processor.build_newsletter_report(
        collected_data=collected_data,
        target_audience=args.audience,
        frequency=args.frequency
    )

    print("[OK] Reporte procesado y validado en esquema estructurado.")

    # 3. Renderizado HTML / Vista previa
    renderer = NewsletterRenderer()
    output_path = renderer.save_html_preview(report, "output/newsletter_preview.html")
    print(f"[DOC] Vista previa generada exitosamente en: file:///{os.path.abspath(output_path)}")

    # 4. Despacho de Correo
    if args.send and not args.dry_run:
        mailer = ResendEmailDelivery()
        recipients = [os.getenv("EMAIL_TO_DPE", "dpe@tudominio.com")]
        print(f"[SEND] Despachando newsletter a: {recipients}")
        mailer.send_newsletter(report, recipients)
    else:
        print("[INFO] Modo simulacion / Dry-run completado. No se realizaron envios por red.")


if __name__ == "__main__":
    main()
