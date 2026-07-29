# Puntualo — Plataforma EdTech de reputación docente

> Documento base para CV y portafolio web.
> Proyecto académico · UNMSM · mayo – julio 2026 · equipo de 4 desarrolladores
> Mi rol: **desarrollador full-stack con foco en backend e IA**

---

## 1. El pitch en un párrafo

Puntualo es una plataforma web donde estudiantes de la Universidad Nacional Mayor de San
Marcos consultan, comparan y califican a sus docentes con datos en lugar de rumores. Un
estudiante entra buscando responder una sola pregunta —"¿con qué profesor llevo este
curso?"— y en lugar de rastrear grupos de WhatsApp encuentra un perfil verificado con
puntajes por dimensión (claridad, dificultad, justicia), reseñas moderadas de compañeros,
un resumen ejecutivo de pros y contras generado con IA, y un asistente conversacional que
responde en lenguaje natural sobre el catálogo real de docentes. Detrás hay una API en
FastAPI, dos pipelines asíncronos con Celery, un sistema RAG sobre PostgreSQL + pgvector,
y un frontend en Next.js 16, todo desplegado en producción sobre una VM de Oracle Cloud
con CI/CD en GitHub Actions.

**Versión de una línea para el CV:**
> Plataforma EdTech de reseñas docentes (Next.js + FastAPI + PostgreSQL) con validación
> automática de perfiles contra 4 fuentes académicas, moderación de contenido y un
> asistente RAG con Cohere + Gemini; desplegada en producción con CI/CD.

---

## 2. El problema que resuelve

Elegir docente es, en la práctica, la decisión que más impacta el semestre de un
estudiante: define cuánto aprende, cuánto sufre y —en el peor caso— si aprueba. Pero la
información con la que se toma esa decisión es la peor posible:

- **Está dispersa.** Vive en grupos de WhatsApp, hilos de Facebook y conversaciones de
  pasillo que se pierden cada ciclo. Cada promoción vuelve a empezar de cero.
- **No es verificable.** Un comentario anónimo puede ser una vendetta, un profesor
  promocionándose, o un caso de homonimia (dos docentes con nombres casi idénticos).
- **No es comparable.** "Dicen que es bueno" no permite contrastar dos opciones ni
  distinguir entre *exigente pero enseña bien* y *fácil pero no aprendes nada*.
- **Tiene ventana corta.** La matrícula dura días. La decisión se toma con prisa y con
  ansiedad.

El resultado es un mercado de información fallido: el estudiante decide con ruido, elige
mal, y el costo lo paga en un ciclo entero. Puntualo existe para convertir ese rumor
disperso en un dato consultable, verificado y comparable.

---

## 3. Qué construimos

### 3.1 Funcionalidades del producto

| Módulo | Qué hace |
|---|---|
| **Autenticación y verificación estudiantil** | Registro con correo institucional, verificación por email, recuperación de contraseña y validación de identidad mediante carnet universitario (subida de imagen con validación de formato y calidad). |
| **Catálogo y buscador de docentes** | Listado paginado con filtros por universidad, facultad, carrera y curso; ordenamiento por puntaje global, claridad o facilidad; búsqueda con estado de validación visible. |
| **Sistema de evaluaciones** | Calificación multidimensional por curso y semestre, comentarios con hashtags normalizados, reacciones y reportes. Puntaje global calculado con pesos configurables. |
| **Validación automática de docentes** | Pipeline asíncrono que contrasta cada perfil creado contra el directorio oficial de la UNMSM, OpenAlex, ORCID y búsqueda web (Tavily), guarda la evidencia encontrada y marca el perfil como validado o no encontrado. |
| **Resumen ejecutivo con IA** | Generación automática de un resumen con pros y contras por docente a partir de sus reseñas publicadas, usando Google Gemini, con umbral mínimo de reseñas para evitar conclusiones sobre muestras pequeñas. |
| **Asistente conversacional (RAG)** | Chatbot que responde preguntas sobre docentes y cursos usando recuperación semántica sobre embeddings + function calling contra la base real, con verificación anti-alucinación. |
| **Comparador de docentes** | Selección de varios profesores, persistencia local y vista comparativa lado a lado por dimensión. |
| **Moderación** | Filtro heurístico de lenguaje ofensivo y términos prohibidos antes de publicar, más cola de reportes con priorización. |
| **Panel administrativo** | Gestión de solicitudes de verificación, reportes sin resolver y métricas de uso de la plataforma. |

### 3.2 Arquitectura

```
┌──────────────────────────────┐
│  Next.js 16 · React 19 · TS  │   Frontend (Vercel)
│  Tailwind 4 · Zustand        │
└──────────────┬───────────────┘
               │ REST + SSE (streaming del chat)
┌──────────────▼───────────────┐
│  FastAPI · Pydantic v2       │   API (VM Oracle Cloud ARM + Caddy)
│  SQLAlchemy async + Alembic  │
└───┬──────────┬───────────┬───┘
    │          │           │
┌───▼────┐ ┌───▼─────┐ ┌───▼──────────────┐
│Postgres│ │  Redis  │ │  Celery worker   │
│pgvector│ │cache +  │ │  + beat          │
│(Supabase)│ broker  │ │                  │
└────────┘ └─────────┘ └───┬──────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │  Pipeline validación docente        │  UNMSM · OpenAlex · ORCID · Tavily
        │  Pipeline resumen IA (Gemini)       │
        │  Recálculo de puntajes              │
        └─────────────────────────────────────┘
```

**Stack completo:** Next.js 16, React 19, TypeScript, TailwindCSS 4, Zustand, Motion ·
FastAPI, Python 3.13, SQLAlchemy 2 (async), Alembic, Pydantic v2, Celery, Redis ·
PostgreSQL 16 con pgvector (Supabase) · Cohere `embed-v4.0`, Google Gemini / Vertex AI ·
Docker, Docker Compose, Caddy, Oracle Cloud (ARM), Vercel · GitHub Actions ·
pytest, Vitest, Playwright, Locust · monorepo con pnpm workspaces.

---

## 4. Métricas de impacto (proyecciones del producto)

> **Nota de honestidad:** Puntualo no llegó a operar con tráfico real masivo, así que las
> cifras de esta sección son **proyecciones y objetivos de producto**, no resultados
> medidos. Se incluyen porque muestran cómo se pensó el valor del sistema y con qué
> instrumentos se mediría. Las métricas *sí medidas* (rendimiento, calidad, usabilidad)
> están en la sección 7.

### 4.1 Métricas que Puntualo busca optimizar

| Métrica | Situación actual (sin Puntualo) | Objetivo con Puntualo | Cómo se mediría |
|---|---|---|---|
| **Tiempo de decisión por docente** | 30–60 min preguntando en grupos y esperando respuestas dispersas | < 3 min: buscar, leer el resumen IA y comparar dos perfiles | Tiempo entre primera búsqueda y vista de comparación (analítica de sesión) |
| **Cobertura informativa** | El estudiante consigue opinión sobre 1–2 docentes de los 4–6 disponibles | Información sobre el 100% de los docentes ofertados en su curso | Docentes con ≥1 reseña / docentes en la malla del ciclo |
| **Confiabilidad de la información** | 0% de verificación: cualquier afirmación vale lo mismo | ≥ 80% de perfiles con validación externa confirmada | `validation_status = validated` sobre el total de perfiles |
| **Reincidencia del conocimiento** | Se pierde cada promoción; cada ciclo se re-pregunta lo mismo | Acumulativo: cada reseña queda disponible para todas las promociones siguientes | Reseñas históricas consultadas por ciclo |
| **Calidad del discurso** | Comentarios sin filtro, con insultos o ataques personales | < 5% de comentarios reportados; 0 publicaciones con lenguaje ofensivo detectable | Reportes resueltos / comentarios publicados |
| **Fricción de entrada** | — | ≥ 60% de visitantes de la landing llegan al buscador sin abandonar | Embudo landing → buscador → registro |
| **Esfuerzo de síntesis** | El estudiante lee 20+ comentarios sueltos y saca conclusiones a mano | 1 resumen ejecutivo con pros/contras por docente (umbral: ≥5 reseñas) | Lecturas de resumen vs. scroll completo de comentarios |
| **Autoservicio del asistente** | — | ≥ 70% de consultas del chatbot resueltas sin que el usuario reformule | Conversaciones de 1 turno / total |

### 4.2 Por qué estas métricas y no otras

El norte del producto no es "cuántas reseñas hay", sino **cuánto mejora la decisión del
estudiante**. Por eso las métricas se agrupan en tres ejes:

1. **Velocidad** — que decidir cueste minutos, no tardes.
2. **Confianza** — que el dato sea verificable (validación externa + moderación), porque
   una plataforma de reseñas sin credibilidad es peor que no tenerla: amplifica el rumor.
3. **Acumulación** — que el conocimiento no se evapore cada promoción. Es el único eje
   que crece solo con el tiempo y el que hace defendible al producto.

---

## 5. Cómo se desarrolló

El proyecto corrió de **mayo a julio de 2026** (≈11 semanas) sobre un monorepo pnpm, con
244 commits y ramas por funcionalidad integradas vía pull request. La evolución tuvo
cuatro fases claras:

### Fase 1 — Fundaciones (mayo, semanas 1–3)
Estructura del monorepo, modelo de datos, autenticación con JWT y el primer CRUD de
docentes con paginación. Se levantó PostgreSQL y Redis en Docker Compose y se estableció
la convención de módulos backend `router / service / schemas` que sostuvo todo el resto
del proyecto.

### Fase 2 — El núcleo del producto (mayo–junio, semanas 3–6)
Módulo de evaluaciones con puntaje multidimensional, comentarios con hashtags, reacciones
y reportes. En paralelo, el pipeline de validación de docentes: investigación previa de
fuentes documentada como spec, y luego implementación con circuit breaker, control de
presupuesto de API y reintentos.

### Fase 3 — La capa de IA (junio–julio, semanas 6–10)
Primero el resumen ejecutivo con Gemini (tarea Celery + hook post-commit + beat de
respaldo). Después el asistente conversacional completo: migración a pgvector, generación
de embeddings con Cohere, retriever semántico con fallback textual, function calling,
streaming por SSE, rate limiting por usuario y una capa de *grounding* que detecta y
corrige nombres inventados antes de responder.

### Fase 4 — Producto y calidad (julio, semanas 10–11)
Rediseño de la landing, login y buscador; comparador de docentes; panel admin;
despliegue en VM Oracle con Caddy y runner self-hosted; y una suite de pruebas completa
(unitarias, integración, e2e, carga, estrés y usabilidad) con CI en GitHub Actions.

### Decisiones técnicas destacadas

- **Todo lo caro va fuera del request.** Validación externa, resúmenes IA y recálculo de
  puntajes corren en Celery. La API nunca bloquea al usuario esperando a un tercero.
- **Circuit breaker por fuente externa.** Si el directorio UNMSM u ORCID falla 5 veces en
  5 minutos, esa fuente se salta sola y se recupera después. Un servicio caído degrada la
  validación, no la tumba.
- **Presupuesto duro para APIs de pago.** La búsqueda web tiene tope mensual de llamadas
  para que un bug no se traduzca en una factura.
- **Grounding antes de responder.** El chatbot valida contra la base que los nombres que
  va a mencionar existen; si detecta uno inventado, ejecuta una ronda de corrección. El
  costo de que un chatbot invente un profesor es la credibilidad del producto entero.
- **Migración de infraestructura de base de datos** cuando el proveedor original impuso
  límites de conexiones incompatibles con Celery + API concurrentes.

---

## 6. Mi contribución

**~97 commits (≈40% del historial del proyecto)**, distribuidos así:

### 6.1 Backend y arquitectura de datos
- Modelo de datos y CRUD completo de docentes, con paginación, manejo de errores y
  migración de identificadores a UUID en toda la capa de servicio.
- Módulo de **evaluaciones**: servicios de evaluación, curso y comentario con lógica de
  puntaje, validación cruzada docente-curso, hashtags normalizados, reacciones y reportes.
- Módulo de **catálogos** (universidades, facultades, carreras, cursos) conectado al flujo
  de alta de docentes con búsqueda en vivo.
- Refactor del esquema de base de datos y modelos para trabajos de IA, términos prohibidos,
  carreras y sesiones de chat.
- Configuración de **pooling de conexiones** para los engines async y sync, y ajuste de la
  concurrencia del worker Celery al resolver saturación de conexiones.
- Siembra de la malla curricular completa de la FISI (Sistemas, Software, Ciencias de la
  Computación) como dataset base del producto.

### 6.2 Pipeline de validación de docentes
- Investigación y documento de diseño sobre fuentes de validación disponibles, previo a
  escribir código.
- Modelo `ProfessorEvidence`, migración y pipeline de validación end-to-end.
- Integración de cuatro fuentes (directorio UNMSM, OpenAlex, ORCID, Tavily) con
  **circuit breaker**, **control de presupuesto** de llamadas, reintentos y logging
  estructurado por etapa.
- Endpoint de revalidación forzada con invalidación de caché y limpieza de evidencia.
- Infraestructura Docker con Redis y Celery para soportar el pipeline.

### 6.3 Capa de IA
**Resumen ejecutivo (Gemini)**
- Generación asíncrona de resúmenes con pros y contras a partir de las reseñas publicadas,
  con guards de calidad (mínimo de reseñas y estado validado), hook post-commit y beat de
  respaldo.
- Visualización del resumen y los pros/contras en el perfil del docente.

**Asistente conversacional RAG (extremo a extremo)**
- Migración a **pgvector** y modelo de embeddings de docentes.
- Cliente de embeddings **Cohere** y generador de embeddings por docente, con tarea
  periódica de refresco.
- Cliente de chat **Gemini** con *tools* y streaming.
- **Retriever semántico** con fallback textual (incluyendo el escapado de comodinos LIKE
  que evitaba resultados corruptos).
- **Function calling**: herramientas de búsqueda, detalle, comparación y búsqueda de cursos.
- Orquestador RAG, prompt de sistema y **capa de grounding** con detección de nombres
  inventados y ronda de corrección; soporte para Vertex AI.
- Endpoints de chat con **streaming SSE**, servicio de sesiones y mensajes, expiración de
  sesión a 48h y **rate limit por usuario y hora**.
- Pruebas del gate de grounding, la detección de nombres inventados y la codificación SSE
  multilínea.

### 6.4 Frontend
- **Interfaz completa del chatbot**: panel responsive con accesibilidad, store de estado
  con manejo de streaming y errores, parser de eventos SSE, lista de mensajes con
  autoscroll inteligente, burbujas con soporte Markdown, input con autoajuste y contador,
  indicador de escritura, botón de nueva conversación y recuperación de sesión.
- **Comparador de docentes** con persistencia en localStorage y badge en la navbar.
- **Rediseño de la landing**, login y registro, con foco en accesibilidad y jerarquía visual.
- **Buscador**: filtros ocultos por defecto, barra reordenada, promedios reales de
  claridad y facilidad en las tarjetas, y ordenamiento conectado al backend.
- Navbar con logo y optimización de **LCP** (`fetchPriority` en el logo).
- Polling condicional del estado de validación en el listado y perfil de docente.

### 6.5 Calidad y corrección de defectos
- Pruebas unitarias de puntaje, ordenamiento por puntaje global, grounding del chatbot y
  codificación SSE.
- Corrección de defectos reales encontrados en integración: contador de pendientes del
  panel admin que no contaba solicitudes reales, `sort_by` de cursos pisado por el orden
  por defecto, ruta de recuperación de sesión del chat, comodines LIKE sin escapar en el
  retriever.

---

## 7. Calidad, pruebas y despliegue (resultados medidos)

Estas cifras sí son mediciones reales tomadas sobre el sistema desplegado:

| Métrica | Resultado |
|---|---|
| Suite de pruebas backend | 125 casos · **96 aprobados, 0 fallidos** |
| Cobertura de líneas | 51% global; **100% en `core/security`**, 94% en rate limiter, 90% en esquemas de auth |
| Pruebas e2e (Playwright) | 3/3 verdes sobre el flujo de autenticación |
| Pruebas de componentes (Vitest) | 8/8 verdes |
| Prueba de carga (Locust, 50 usuarios concurrentes, 3 min) | **2 631 peticiones · 14.64 req/s · 0% de error · p95 1 400 ms** |
| Usabilidad (SUS) | **87.5 / 100** — categoría "excelente" (>68 es sobre el promedio) |
| Defectos documentados bajo carga | 2, ambos trazados a saturación del pool de conexiones, con mitigación propuesta |

**Despliegue:** backend dockerizado en una VM ARM de Oracle Cloud detrás de Caddy (HTTPS),
con despliegue automático vía GitHub Actions y runner self-hosted en cada push a `main`
que toque el backend; frontend en Vercel; base de datos gestionada con connection pooler.
El CI ejecuta la suite de pruebas sobre SQLite en memoria en cada push y pull request.

---

## 8. ¿Individual o grupal?

**Desarrollo grupal.** Puntualo fue un proyecto académico de un equipo de **4
desarrolladores** en la UNMSM, con reparto de áreas: frontend, backend, base de datos y
pruebas.

**Mi rol dentro del equipo:** entré asignado a backend y terminé cubriendo el eje
técnico más transversal del proyecto. Fui el **mayor contribuyente del repositorio**
(≈40% de los commits) y **el único responsable de la capa de inteligencia artificial de
extremo a extremo** — desde la migración a pgvector y la generación de embeddings hasta la
interfaz de chat en React. También construí el pipeline de validación de docentes completo
(investigación, diseño, implementación y resiliencia) y el módulo de evaluaciones, que es
el núcleo funcional del producto.

**Cómo trabajamos:** ramas por funcionalidad, pull requests hacia `main`, CI obligatorio
en cada push, y specs escritas antes de las funcionalidades de mayor riesgo (la
investigación de fuentes de validación se documentó y aprobó antes de escribir una línea
de pipeline). La documentación técnica del backend —arranque, variables de entorno,
troubleshooting de Celery, circuit breakers— la escribí para que cualquier integrante
pudiera levantar el sistema completo sin depender de mí.

**Lo que aporté más allá del código:** las decisiones de resiliencia (circuit breakers,
presupuesto de APIs de pago, grounding anti-alucinación) no estaban en el alcance pedido.
Las propuse e implementé porque un proyecto que integra cuatro APIs externas y dos modelos
de lenguaje falla de formas que un CRUD no falla, y el equipo necesitaba que esas fallas
fueran degradaciones y no caídas.

---

## 9. Material listo para copiar

### 9.1 Bullets para el CV

**Puntualo — Desarrollador Full-Stack (Backend / IA)** · may 2026 – jul 2026 · Proyecto académico en equipo (4 desarrolladores)

- Diseñé e implementé un **asistente conversacional RAG** de extremo a extremo sobre
  PostgreSQL + pgvector (embeddings con Cohere, generación con Gemini/Vertex AI), con
  function calling, streaming SSE, rate limiting y una capa de *grounding* que detecta y
  corrige alucinaciones de nombres antes de responder.
- Construí un **pipeline asíncrono de validación de perfiles docentes** contra 4 fuentes
  externas (directorio institucional, OpenAlex, ORCID, búsqueda web) con Celery, circuit
  breaker por fuente, control de presupuesto de API y reintentos con logging estructurado.
- Desarrollé el **módulo de evaluaciones** —núcleo del producto—: puntaje multidimensional,
  comentarios con hashtags normalizados, reacciones, reportes y moderación previa a la
  publicación.
- Implementé la **interfaz de chat en React 19 / Next.js 16**: streaming SSE, autoscroll
  inteligente, recuperación de sesión, soporte Markdown y accesibilidad.
- Diagnostiqué y resolví cuellos de botella de **rendimiento en producción** (pooling de
  conexiones y concurrencia de workers) sobre evidencia de pruebas de carga con Locust:
  0% de error y p95 de 1.4 s con 50 usuarios concurrentes.
- Contribuí **~40% de los commits** del repositorio (≈97 de 244), con pruebas unitarias y
  de integración versionadas y ejecutadas en CI.

### 9.2 Descripción corta para portafolio web (~60 palabras)

> Plataforma EdTech que ayuda a estudiantes universitarios a elegir docentes con datos en
> lugar de rumores: perfiles validados contra fuentes académicas, reseñas moderadas,
> resúmenes de pros y contras generados con IA y un asistente conversacional sobre el
> catálogo real. Trabajé en el backend (FastAPI, Celery, PostgreSQL) y construí toda la
> capa de IA, incluido el sistema RAG y su interfaz.

### 9.3 Palabras clave para filtros ATS

`Python` · `FastAPI` · `SQLAlchemy` · `Alembic` · `Celery` · `Redis` · `PostgreSQL` ·
`pgvector` · `RAG` · `Embeddings` · `LLM` · `Cohere` · `Google Gemini` · `Vertex AI` ·
`Function Calling` · `Server-Sent Events` · `TypeScript` · `React` · `Next.js` ·
`TailwindCSS` · `Zustand` · `Docker` · `Docker Compose` · `Caddy` · `Oracle Cloud` ·
`Vercel` · `GitHub Actions` · `CI/CD` · `pytest` · `Playwright` · `Vitest` · `Locust` ·
`Monorepo` · `pnpm` · `REST API` · `JWT` · `Arquitectura de microservicios asíncronos`

### 9.4 Historia para entrevista (STAR)

**Situación:** el chatbot respondía con seguridad sobre profesores que no existían en la
base. En una plataforma cuyo valor entero es la credibilidad del dato, eso no era un bug
menor: invalidaba el producto.

**Tarea:** garantizar que ninguna respuesta mencionara entidades inexistentes, sin
sacrificar la fluidez conversacional ni convertir el chat en un buscador rígido.

**Acción:** implementé una capa de *grounding* que, antes de emitir la respuesta, extrae
las entidades mencionadas y las contrasta contra la base real. Si detecta un nombre
inventado, ejecuta una ronda de corrección con el contexto verificado en lugar de
descartar la respuesta. Lo complementé con function calling —búsqueda, detalle,
comparación y cursos— para que el modelo consultara datos reales en vez de recordarlos, y
cubrí el gate con pruebas unitarias específicas.

**Resultado:** las respuestas quedaron ancladas al catálogo real, con pruebas automatizadas
que protegen el comportamiento ante futuros cambios de prompt o de modelo.

---

## 10. Qué aprendí

- **Los sistemas con IA fallan distinto.** Un CRUD falla con un 500; un LLM falla dando
  una respuesta perfectamente redactada y falsa. Eso obliga a diseñar verificación como
  parte del sistema, no como un extra.
- **Las integraciones externas se diseñan asumiendo que van a caer.** Circuit breakers,
  presupuestos y degradación elegante no son sobreingeniería cuando dependes de cuatro
  servicios que no controlas.
- **Medir antes de optimizar.** El cuello de botella de rendimiento no era el que
  suponíamos: la prueba de carga lo ubicó en el pool de conexiones, y el arreglo fue de
  configuración, no de código.
- **La documentación es infraestructura de equipo.** Escribir el arranque y el
  troubleshooting del backend eliminó la dependencia de que yo estuviera disponible para
  que otros trabajaran.

---

*Última actualización: 28 de julio de 2026.*
