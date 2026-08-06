from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class NewsItem(BaseModel):
    """Modelo para una nota de noticia individual."""
    title: str = Field(..., description="Título representativo de la nota")
    content: str = Field(..., description="Resumen conciso de 2 a 3 renglones")
    url: str = Field(..., description="Enlace a la fuente original de la nota")
    source_domain: str = Field(..., description="Dominio verificado de la fuente")
    category: str = Field(..., description="Categoría asignada a la nota")


class NewsletterSection(BaseModel):
    """Modelo para una sección temática del newsletter."""
    section_id: str
    section_title: str
    items: List[NewsItem] = []


class ExecutiveSummary(BaseModel):
    """Resumen en bullet points para Dirección General y DPE."""
    bullets: List[str] = Field(default_factory=list, description="Bullet points clave de la edición")


class NewsletterReport(BaseModel):
    """Modelo completo del reporte / newsletter generado."""
    title: str = Field("Newsletter de Inteligencia de Mercado y Salud", description="Título principal")
    edition_date: str = Field(..., description="Fecha de edición (ej. 28 de Agosto, 2026)")
    frequency: str = Field("Semanal", description="Frecuencia del reporte: Semanal o Mensual")
    target_audience: str = Field("DPE", description="Audiencia objetivo: DPE, Departamentos o DG")
    
    nota_principal: Optional[NewsItem] = None
    competencia: List[NewsItem] = Field(default_factory=list)
    sector_publico: List[NewsItem] = Field(default_factory=list)
    canales_informacion: List[NewsItem] = Field(default_factory=list)
    sector_privado: List[NewsItem] = Field(default_factory=list)
    resumen_ejecutivo: List[str] = Field(default_factory=list)

    is_verified_by_guardrails: bool = Field(True, description="Indica si pasó los controles de seguridad")
