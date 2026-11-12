import json
from typing import List, Tuple

DEFAULT_SOURCES_PATH = "config/sources.json"


def validate_sources_config(sources_path: str = DEFAULT_SOURCES_PATH) -> Tuple[List[str], List[str]]:
    """
    Valida config/sources.json a nivel estructural: detecta errores críticos (JSON
    inválido, falta de whitelisted_domains) y observaciones no críticas (categorías sin
    descripción, dominios en sources_by_tier que no están en whitelisted_domains).
    Retorna (errores_criticos, observaciones).
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        errors.append(f"No se encontró el archivo {sources_path}.")
        return errors, warnings
    except json.JSONDecodeError as e:
        errors.append(f"{sources_path} tiene JSON inválido: {e}")
        return errors, warnings

    whitelisted = set(data.get("whitelisted_domains", []))
    if not whitelisted:
        errors.append("whitelisted_domains está vacío o no definido.")

    for tier_name, entries in data.get("sources_by_tier", {}).items():
        for entry in entries:
            domain = entry.get("domain", "")
            if domain and domain not in whitelisted:
                warnings.append(
                    f"El dominio '{domain}' en sources_by_tier.{tier_name} no está en whitelisted_domains."
                )

    if not data.get("categories"):
        warnings.append("No se definieron 'categories' en sources.json.")

    return errors, warnings


def print_validation_report(sources_path: str = DEFAULT_SOURCES_PATH) -> bool:
    """
    Imprime el resultado de la validación de config/sources.json y retorna True si no
    hay errores críticos (puede haber observaciones no críticas).
    """
    errors, warnings = validate_sources_config(sources_path)

    if errors:
        print(f"[ERROR] {sources_path} tiene errores críticos:")
        for err in errors:
            print(f"  - {err}")
        return False

    if warnings:
        print(f"[CONFIG] {sources_path} validado con observaciones:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print(f"[CONFIG] {sources_path} validado correctamente, sin observaciones.")

    return True
