# Plan de Trabajo - Agente de Inteligencia de Mercado y Sector Salud

## Objetivo
En este plan de trabajo se busca delimitar cuáles son las necesidades que serán satisfechas, así como también los requerimientos para un correcto funcionamiento de la herramienta.

Se buscará crear un agente con parámetros de seguridad delimitados que ayuden a recabar información de carácter público de manera automática —mensualmente en una primera etapa y posteriormente semanalmente— con la mira de recibir un digerido de información crítica constante que apoye al área de DPE.

---

## Características

> 📌 **Newsletter Automatizado**  
> Creación de un newsletter que recopile información importante y latente para el análisis continuo del mercado, competidores y noticias de alto valor para el sector salud (salud general y específico para laboratorio).

- Se implementará un agente de IA con los debidos parámetros de seguridad para evitar alucinaciones y mantenerlo enfocado en la información relevante.
- El agente generará un reporte semanal enviado vía correo electrónico a ciertas áreas, y posteriormente mensual para Dirección General.
- El objetivo principal es mantenernos en vanguardia del sector.

---

## Formato Esperado
Una pequeña infografía de información condensada:
- **Título por nota**
- **2–3 renglones máximo de contenido**
- **Enlace a la nota completa al pie de cada sección**
- **Estructura por semana:**
  1. Nota principal (mayor relevancia)
  2. Notas de competencia
  3. Sector público salud
  4. Canales de información (redes, médicos, YouTube)
  5. Sector privado salud
  6. Resumen en *bullet points*

---

## Alcance

| Fase | Destinatario | Descripción |
| :--- | :--- | :--- |
| **Beta** | DPE | Entorno de prueba en correos internos, construcción iterativa del reporte. |
| **Expansión** | Departamentos clave | Entrega a áreas donde la información apoye la toma de decisiones. |
| **Producción** | Dirección General | Sistema probado y validado para Dirección General (DG). |

---

## Inteligencia Artificial a Utilizar

| Herramienta | Rol | Justificación |
| :--- | :--- | :--- |
| **Google Gemini** | Scrapper / Recolección de datos | Especialización en búsqueda y razonamiento web. |
| **Claude (Anthropic)** | Procesador y redactor | Especialización en razonamiento y síntesis de texto. |

*Nota: No se dejará que el agente improvise fuentes; trabajará exclusivamente con las fuentes enlistadas y aprobadas.*

### Opciones de Envío Automatizado
- **Rutina por Google Apps Script:** Herramienta existente en plan gratuito (bajo volumen de envíos).
- **Resend:** [https://resend.com/](https://resend.com/)

---

## Parámetros de Seguridad (Guardrails)

> 🔒 **Restricciones y Controles**  
> Especificar los guardrails necesarios para la elaboración del proceso y plasmarlos en un diagrama que muestre restricciones y puntos de control en cada paso del flujo del agente.

- [ ] Definir fuentes permitidas (lista blanca de URLs y dominios)
- [ ] Establecer restricciones de contenido (sin opinión, sin fuentes no verificadas)
- [ ] Definir formato de salida fijo (estructura de newsletter)
- [ ] Crear diagrama de flujo con restricciones por etapa (por realizarse)
- [ ] Validación humana antes del primer envío oficial

---

## Timeline

> ⏳ **Estatus:** Pendiente de visto bueno. Las fechas inician una vez aprobado el proyecto.  
> **Calendario comprimido:** Primer envío a DPE en agosto, entrega a DG en la primera semana de octubre.

### Agosto 2026

| Semana | Fecha | Actividad |
| :--- | :--- | :--- |
| **Sem 2** | 11/ago | Kick-off: revisión de alcance y objetivos |
| | 12/ago | Configuración base del agente + definición de fuentes |
| | 13/ago | Configuración base del agente + definición de fuentes |
| | 14/ago | Diseño de guardrails (restricciones de contenido) |
| | 15/ago | Diseño de guardrails (formato de salida fijo) |
| | 16/ago | Documentación de avances Sem 2 |
| **Sem 3** | 18/ago | Entrenamiento del agente (instrucciones y tono) |
| | 19/ago | Entrenamiento del agente (validación de fuentes) |
| | 20/ago | Entrenamiento del agente (formato newsletter) |
| | 21/ago | Primera prueba de generación interna |
| | 22/ago | Ajustes post-prueba + validación humana |
| | 23/ago | Documentación de avances Sem 3 |
| **Sem 4** | 25/ago | Segunda prueba interna + refinamiento |
| | 26/ago | Configuración del envío automatizado |
| | 27/ago | Prueba de envío automatizado (correo interno) |
| | 28/ago | 🚀 **Primer envío oficial DPE** |
| | 29/ago | Recolección de feedback DPE |
| | 30/ago | Documentación de avances Sem 4 |

### Septiembre 2026

| Semana | Fecha | Actividad |
| :--- | :--- | :--- |
| **Sem 1** | 1/sep | Ajustes según feedback DPE |
| | 2/sep | Ajustes según feedback DPE |
| | 3/sep | Segundo envío oficial DPE |
| | 4/sep | Revisión de calidad post-envío |
| | 5/sep | Iteración y mejora del agente |
| | 6/sep | Documentación de avances Sem 1 |
| **Sem 2** | 8/sep | Tercer envío DPE |
| | 9/sep | Evaluación general de calidad beta |
| | 10/sep | Identificación de departamentos destino |
| | 11/sep | Envío piloto a departamentos clave |
| | 12/sep | Recolección de feedback departamentos |
| | 13/sep | Documentación de avances Sem 2 |
| **Sem 3** | 15/sep | Ajustes finales según feedback de departamentos |
| | 16/sep | Refinamiento del formato final del newsletter |
| | 17/sep | Inicio preparación entregable DG |
| | 18/sep | Compilación de métricas y resultados beta |
| | 19/sep | Redacción de reporte ejecutivo para DG |
| | 20/sep | Documentación de avances Sem 3 |
| **Sem 4** | 22/sep | Redacción de reporte ejecutivo para DG |
| | 23/sep | Revisión interna del entregable |
| | 24/sep | Aprobación interna DPE |
| | 25/sep | Preparación de presentación para DG |
| | 26/sep | Ensayo de presentación |
| | 27/sep | Ajustes finales al entregable |

### Primera Semana de Octubre 2026

| Semana | Fecha | Actividad |
| :--- | :--- | :--- |
| **Sem 1 · Cierre** | 29/sep | Revisión final del entregable DG |
| | 30/sep | Confirmación de fecha de presentación con DG |
| | 1/oct | 🏁 **Entrega oficial a Dirección General** |
| | 2/oct | Presentación y revisión con DG |
| | 3/oct | Recepción de feedback DG + cierre de fase |
| | 4/oct | Archivo del proyecto y documentación final |

---

## Notas Adicionales
1. El formato del newsletter semanal se basa en la estructura: **nota principal → competencia → sector público salud → canales de información → sector privado salud → resumen en bullet points**.
2. El volumen de envíos inicial es bajo, por lo que un plan gratuito de envío es viable en esta etapa.
3. El diagrama de parámetros de seguridad está pendiente de elaboración.
