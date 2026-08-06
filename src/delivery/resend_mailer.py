import os
from typing import Optional, List
from src.models import NewsletterReport
from src.newsletter.renderer import NewsletterRenderer


class ResendEmailDelivery:
    """Servicio de envío de correo automatizado mediante Resend API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        self.renderer = NewsletterRenderer()

    def send_newsletter(
        self,
        report: NewsletterReport,
        recipient_emails: List[str],
        sender_email: Optional[str] = None
    ) -> bool:
        """Envia el boletín informativo a la lista de destinatarios."""
        sender = sender_email or os.getenv("EMAIL_FROM", "onboarding@resend.dev")
        html_body = self.renderer.render_html(report)

        if not self.api_key:
            print(f"[DRY-RUN / SIMULACIÓN] Envió omitido (Sin RESEND_API_KEY). Destinatarios: {recipient_emails}")
            print(f"[DRY-RUN] Asunto: {report.title} - Edición {report.edition_date}")
            return True

        try:
            import resend
            resend.api_key = self.api_key
            params = {
                "from": sender,
                "to": recipient_emails,
                "subject": f"📌 {report.title} | {report.edition_date}",
                "html": html_body
            }
            email_res = resend.Emails.send(params)
            print(f"[INFO] Correo enviado exitosamente via Resend ID: {email_res.get('id')}")
            return True
        except Exception as e:
            print(f"[ERROR] Error despachando correo via Resend: {e}")
            return False
