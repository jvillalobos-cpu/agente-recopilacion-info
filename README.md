# Agente de Inteligencia de Mercado y Sector Salud

Este proyecto implementa un agente autónomo asistido por inteligencia artificial (Google Gemini y Anthropic Claude) diseñado para recopilar, filtrar y estructurar información del sector salud en México y Latinoamérica bajo estrictos parámetros de seguridad (Guardrails).

## 📌 Características
- **Recopilación Autónoma**: Búsqueda periódica de noticias clave de mercado, competencia y regulación pública/privada.
- **Lista Blanca Estricta (Guardrails)**: Solo procesa e incluye información proveniente de dominios y sitios previamente autorizados (`config/sources.json`).
- **Formato Infografía / Newsletter**: Salida visual y responsiva lista para ser enviada por correo electrónico a DPE y Dirección General.
- **Formato de Salida Rígido**:
  1. Nota principal (mayor relevancia)
  2. Notas de competencia
  3. Sector público salud
  4. Canales de información (redes, médicos, YouTube)
  5. Sector privado salud
  6. Resumen en bullet points

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
python main.py --dry-run
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
│   ├── sources.json          # Lista blanca de dominios y categorías permitidas
│   └── guardrails.yaml       # Restricciones estricta de contenido y formato
├── docs/
│   └── plan_de_trabajo.md    # Especificación y plan de trabajo original
├── src/
│   ├── collector/            # Módulo de recolección y validación de fuentes
│   ├── processor/            # Síntesis e IA con Guardrails
│   ├── newsletter/           # Renderizador de plantillas HTML
│   ├── delivery/             # Conector de envío de correo via Resend API
│   └── models.py             # Esquemas de datos Pydantic
├── templates/
│   └── newsletter.html       # Plantilla HTML del newsletter ejecutivo
├── tests/                    # Pruebas unitarias automatizadas
├── main.py                   # Punto de entrada de la aplicación CLI
└── requirements.txt
```

---

## 🧪 Pruebas Automatizadas
Ejecuta la suite de pruebas unitarias para validar las restricciones de lista blanca y renderizado:
```bash
pytest
```
