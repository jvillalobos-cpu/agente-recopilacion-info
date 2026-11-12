import os
import re
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from src.models import NewsletterReport


def _bold_filter(text: str) -> Markup:
    """Convierte **texto** (markdown simple) en <strong>texto</strong>, escapando el resto."""
    escaped = Markup.escape(text)
    converted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", str(escaped))
    return Markup(converted)


class NewsletterRenderer:
    """Renderizador Jinja2 para compilar el boletín de noticias en HTML responsivo."""

    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        self.env.filters["bold"] = _bold_filter

    def render_html(self, report: NewsletterReport, template_name: str = "newsletter.html") -> str:
        """Renderiza el objeto NewsletterReport en una cadena HTML."""
        template = self.env.get_template(template_name)
        return template.render(report=report)

    def save_html_preview(self, report: NewsletterReport, output_path: str = "output/newsletter_preview.html") -> str:
        """Guarda la vista previa local del boletín para inspección previa al envío."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        html_content = self.render_html(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return output_path
