# Agente de Inteligencia de Mercado y Sector Salud

Este proyecto implementa un agente autónomo asistido por inteligencia artificial (Google Gemini y Anthropic Claude) diseñado para recopilar, filtrar y estructurar información del sector salud en México y Latinoamérica bajo estrictos parámetros de seguridad (Guardrails) y una disciplina de **cero alucinación**: toda nota requiere una fecha de publicación real y verificable, y solo se incluye información de dominios previamente autorizados.

## 📌 Características
- **Recopilación Autónoma**: Búsqueda periódica de noticias clave de mercado, competencia y regulación pública/privada.
- **Monitoreo de YouTube Oficial**: Conector basado en la YouTube Data API v3 (sin scraping de HTML) que revisa videos recientes de canales oficiales configurados en `config/sources.json` (`canales_youtube_oficiales`), p. ej. COFEPRIS, ADLM y Baja Health Cluster.
- **Curación Manual de Redes Sociales**: Para personas/empresas que solo publican en Instagram, X o LinkedIn (sin blog propio), el analista registra el post en `config/manual_posts.json` (URL, tema, fecha) y el agente lo integra al boletín con las mismas reglas de lista blanca y recencia que cualquier otra fuente — sin scraping automatizado de redes sociales.
- **Detección de Nuevos Competidores vía CLUES (DGIS)**: Compara el catálogo oficial de establecimientos de salud de la Secretaría de Salud (CLUES) contra el snapshot de la corrida anterior para detectar automáticamente nuevos laboratorios/clínicas privadas registrados en Baja California, en vez de depender de hallazgos manuales.
- **Seguimiento de la Mañanera Presidencial**: La conferencia matutina de la Presidencia suele dedicar un bloque de salud los martes (IMSS, ISSSTE, IMSS-Bienestar, COFEPRIS). Se da seguimiento vía la versión estenográfica oficial en `gob.mx/presidencia` y cobertura de prensa de lista blanca, incorporando los anuncios relevantes como notas curadas.
- **Fuentes permanentes monitoreadas**: Abbott Laboratories, QuidelOrtho, Quest Diagnostics, Epic Systems Corporation y eHealth Reporter se consultan en cada corrida como fuentes fijas, además de las búsquedas temáticas por categoría.
- **IA en Salud y Laboratorios**: Categoría dedicada a inteligencia artificial aplicada específicamente a diagnóstico y medicina de laboratorio (no IA genérica) — startups, modelos, gobernanza regulatoria y adopción clínica.
- **Lista Blanca Estricta (Guardrails)**: Solo procesa e incluye información proveniente de dominios y sitios previamente autorizados (`config/sources.json`). Todo rechazo (dominio no autorizado, nota desactualizada) queda registrado en `logs/security_rejections.jsonl` para auditoría.
- **Filtro de Recencia y Deduplicación**: Cada nota requiere `published_date` verificable; se descarta si excede la ventana permitida (10 días en corte Semanal, 35 en Mensual) o si es un casi-duplicado de otra nota ya incluida.
- **Formato Infografía / Newsletter**: Salida visual mobile-first (pensada para compartirse/leerse en WhatsApp), con el resumen ejecutivo como primera sección.
- **Formato de Salida**:
  1. Resumen ejecutivo (bullet points, al inicio)
  2. Nota principal (mayor relevancia)
  3. Notas de competencia
  4. Sector público salud
  5. IA en salud y laboratorios
  6. Canales de información (redes, médicos, YouTube)
  7. Sector privado salud

---

## 🛠️ Instalación y Uso

### 1. Requisitos Previos
- Python 3.10 o superior

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configuración del Archivo `.env`
Copia la plantilla `.env.example` a `.env` y configura tus API Keys:
```bash
cp .env.example .env
```

### 4. Ejecución en Modo Prueba Local (Dry Run)
Para recopilar noticias, procesar el boletín y generar la vista previa HTML sin realizar envíos por correo:
```bash
python main.py --dry-run --frequency Mensual
```
La vista previa se abrirá o guardará en: `output/newsletter_preview.html`.

### 5. Ejecución con Envío Real por Correo (Resend)
```bash
python main.py --send --audience DPE
```

---

## 📂 Estructura del Proyecto

```text
├── config/
│   ├── sources.json          # Lista blanca de dominios, categorías y fuentes permanentes
│   ├── manual_posts.json     # Notas curadas a mano (redes sociales, comunicados oficiales)
│   └── guardrails.yaml       # Restricciones estricta de contenido y formato
├── docs/
│   └── plan_de_trabajo.md    # Especificación y plan de trabajo original
├── src/
│   ├── collector/            # Recolección, validación de fuentes y guardrails
│   │   ├── whitelist_validator.py   # Lista blanca + log de rechazos
│   │   ├── recency_filter.py        # Guardrail de recencia (cero alucinación)
│   │   ├── deduplicator.py          # Deduplicación por URL/título
│   │   ├── security_log.py          # Log JSONL auditable de rechazos
│   │   ├── config_validator.py      # Validación estructural de sources.json
│   │   ├── manual_curation.py       # Curación manual de redes sociales
│   │   ├── clues_collector.py       # Detección de competidores vía catálogo CLUES
│   │   ├── mananera_collector.py    # Bloque de salud de la mañanera (martes)
│   │   └── youtube_collector.py     # YouTube Data API v3
│   ├── processor/             # Síntesis y guardrails de contenido
│   ├── newsletter/            # Renderizador de plantillas HTML
│   ├── delivery/               # Conector de envío de correo via Resend API
│   └── models.py               # Esquemas de datos Pydantic
├── templates/
│   └── newsletter.html       # Plantilla HTML mobile-first del newsletter ejecutivo
├── tests/                    # Pruebas unitarias automatizadas
├── main.py                   # Punto de entrada de la aplicación CLI
└── requirements.txt
```

---

## 🧪 Pruebas Automatizadas
Ejecuta la suite de pruebas unitarias para validar las restricciones de lista blanca, recencia, deduplicación y renderizado:
```bash
pytest
```
