from typing import List, Optional
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """Modelo para una nota de noticia individual."""
    title: str = Field(..., description="Título representativo de la nota")
    content: str = Field(..., description="Resumen conciso de 2 a 3 renglones")
    url: str = Field(..., description="Enlace a la fuente original de la nota")
    source_domain: str = Field(..., description="Dominio verificado de la fuente")
    category: str = Field(..., description="Categoría asignada a la nota")
    published_date: Optional[str] = Field(
        None, description="Fecha de publicación de la nota en formato ISO (YYYY-MM-DD), usada para el filtro de recencia"
    )


class NewsletterSection(BaseModel):
    """Modelo para una sección temática del newsletter."""
    section_id: str
    section_title: str
    items: List[NewsItem] = []


class ExecutiveSummary(BaseModel):
    """Resumen en bullet points para Dirección General y DPE."""
    bullets: List[str] = Field(default_factory=list, description="Bullet points clave de la edición")


class ExecutiveBullet(BaseModel):
    """Punto del resumen ejecutivo enlazado a la nota que lo sustenta."""
    text: str = Field(..., description="Texto del bullet, con la etiqueta de categoría en negritas")
    url: Optional[str] = Field(None, description="Enlace a la nota fuente que respalda el bullet")
    source_domain: Optional[str] = Field(None, description="Dominio de la fuente que respalda el bullet")


class NewsletterReport(BaseModel):
    """Modelo completo del reporte / newsletter generado."""
    title: str = Field("Newsletter de Inteligencia de Mercado y Salud", description="Título principal")
    edition_date: str = Field(..., description="Fecha de edición (ej. 28 de Agosto, 2026)")
    frequency: str = Field("Semanal", description="Frecuencia del reporte: Semanal o Mensual")
    target_audience: str = Field("DPE", description="Audiencia objetivo: DPE, Departamentos o DG")

    nota_principal: Optional[NewsItem] = None
    competencia: List[NewsItem] = Field(default_factory=list)
    sector_publico: List[NewsItem] = Field(default_factory=list)
    ia_salud_laboratorios: List[NewsItem] = Field(default_factory=list)
    canales_informacion: List[NewsItem] = Field(default_factory=list)
    sector_privado: List[NewsItem] = Field(default_factory=list)
    resumen_ejecutivo: List[ExecutiveBullet] = Field(default_factory=list)

    editor_name: str = Field("Dirección de Proyectos Estratégicos", description="Responsable editorial del boletín")
    editor_role: str = Field("Certus Laboratorio", description="Cargo / área del responsable editorial")

    is_verified_by_guardrails: bool = Field(True, description="Indica si pasó los controles de seguridad")
