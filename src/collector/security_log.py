import os
import json
import datetime

SECURITY_LOG_PATH = "logs/security_rejections.jsonl"


def log_rejection(event_type: str, reason: str, title: str = "", url: str = "", category: str = "",
                   log_path: str = SECURITY_LOG_PATH) -> None:
    """
    Registra en un archivo JSONL (append-only) cada nota rechazada por un guardrail
    (dominio no autorizado, nota desactualizada, duplicado, etc.), para dejar rastro
    auditable de las decisiones de "cero alucinación" tomadas por el agente.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "reason": reason,
        "title": title,
        "url": url,
        "category": category,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
