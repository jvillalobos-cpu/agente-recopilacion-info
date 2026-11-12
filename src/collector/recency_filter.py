import datetime
from typing import List, Optional, Tuple
from src.models import NewsItem
from src.collector.security_log import log_rejection


def is_recent(item: NewsItem, max_age_days: int, reference_date: Optional[datetime.date] = None) -> Tuple[bool, str]:
    """
    Determina si una nota está dentro de la ventana de recencia permitida. Una nota sin
    published_date verificable se rechaza siempre (guardrail de cero alucinación: no se
    puede confiar en una fecha que no fue provista).
    """
    reference_date = reference_date or datetime.date.today()

    if not item.published_date:
        return False, "sin published_date verificable"

    try:
        pub_date = datetime.date.fromisoformat(item.published_date)
    except ValueError:
        return False, f"published_date con formato inválido: '{item.published_date}'"

    age_days = (reference_date - pub_date).days
    if age_days < 0:
        return False, f"published_date en el futuro respecto a la fecha de referencia ({item.published_date})"
    if age_days > max_age_days:
        return False, f"nota de hace {age_days} días, excede la ventana de {max_age_days} días"

    return True, ""


def filter_recent_items(
    items: List[NewsItem],
    max_age_days: int,
    reference_date: Optional[datetime.date] = None
) -> List[NewsItem]:
    """Filtra una lista de notas, conservando únicamente las que están dentro de la ventana de recencia."""
    kept = []
    for item in items:
        ok, reason = is_recent(item, max_age_days, reference_date)
        if ok:
            kept.append(item)
        else:
            log_rejection(
                event_type="nota_desactualizada",
                reason=reason,
                title=item.title,
                url=item.url,
                category=item.category,
            )
    return kept
