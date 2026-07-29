# ContentSpark — Resumen de proyecto para CV / Portafolio

> Documento de referencia narrativo para redactar CV y portafolio web. **No se sube al repositorio.**

---

## 1. Qué es ContentSpark

ContentSpark es una **plataforma SaaS para creadores de contenido** que combina recuperación semántica de información (RAG), agentes conversacionales basados en LLM y planificación de contenido asistida por IA. Nació como una herramienta RAG local y evolucionó hacia una arquitectura SaaS completa: backend en FastAPI con base de datos relacional propia, frontend en Next.js, autenticación gestionada y una base de conocimiento vectorial consultable en tiempo real.

El problema que resuelve: los creadores de contenido (TikTok, Reels, Shorts, LinkedIn) suelen consumir decenas de guías y frameworks sobre creación de contenido, pero pierden ese conocimiento y no tienen forma de aplicarlo de manera personalizada a su propio nicho, tono y audiencia. ContentSpark centraliza ese conocimiento en una base vectorial curada y lo combina con el perfil del creador para dar respuestas contextualizadas, en lugar de respuestas genéricas de un LLM sin contexto.

**Público objetivo:** creadores de contenido intermedios-avanzados en Latinoamérica y España (interfaz en español).

---

## 2. Tipo de desarrollo

**Proyecto de desarrollo individual.** Todo el diseño de arquitectura, backend, frontend, pipeline de RAG y decisiones técnicas fueron realizados en solitario (confirmado por el historial de control de versiones: un único autor en todos los commits del repositorio). Es un proyecto personal construido para explorar y demostrar competencias en arquitectura de aplicaciones SaaS con IA aplicada — útil para presentarlo como muestra de capacidad de ejecución end-to-end (backend, frontend, infraestructura de datos y diseño de producto) sin equipo de apoyo.

*(Si en algún momento hubo colaboración externa —por ejemplo, feedback de diseño, mentoría o pair programming puntual— avísame y lo agrego como matiz.)*

---

## 3. Mi rol y responsabilidades

Al ser un desarrollo individual, el rol cubierto fue de **full-stack / AI engineer** end-to-end:

- Diseño de arquitectura de la plataforma (separación backend/frontend, modelo de datos, contratos de API).
- Diseño e implementación del pipeline de RAG (ingesta, chunking, embeddings, recuperación, generación).
- Desarrollo backend en Python (FastAPI, SQLAlchemy async, Alembic, LangGraph).
- Desarrollo frontend en TypeScript (Next.js, React, gestión de estado con Zustand).
- Integración de servicios externos de IA (Groq, Google Gemini) y de infraestructura (Supabase, Qdrant).
- Definición de convenciones de código, estructura de carpetas por *features* y documentación técnica del proyecto (specs y planes de implementación versionados).
- Escritura de tests automatizados (backend con pytest, frontend con Vitest + Testing Library) e integración de un pipeline de CI (lint + type-check) en GitHub Actions.

---

## 4. Stack tecnológico

**Frontend**
- Next.js 16 (App Router) + React 19 + TypeScript
- Tailwind CSS 4, diseño propio con estética *glassmorphism*
- Zustand (estado global de sesiones de chat)
- Supabase Auth (`@supabase/supabase-js`, `@supabase/ssr`) — email/password + Google OAuth
- react-markdown + remark-gfm para renderizado de respuestas
- Testing: Vitest + Testing Library

**Backend**
- FastAPI + Uvicorn (Python 3.10+)
- SQLAlchemy 2.0 (async, con `asyncpg`) + Alembic para migraciones versionadas
- Pydantic / Pydantic Settings para validación y configuración
- LangChain + LangGraph para orquestación de agentes y pipeline CRAG
- Testing: pytest, pytest-asyncio, pytest-mock, httpx

**Inteligencia artificial**
- LLM de generación: Groq (Llama 3.1 8B) — inferencia de baja latencia
- Embeddings: Google Gemini (`gemini-embedding-001`, 3072 dimensiones)
- Orquestación de agentes: LangGraph (StateGraph)
- Búsqueda web de respaldo: DuckDuckGo Search (fallback cuando el contexto interno no es suficiente)

**Datos e infraestructura**
- PostgreSQL (vía Supabase) como base de datos relacional
- Qdrant (vector store en la nube) para búsqueda semántica
- n8n (automatización de flujos, integración con Google Calendar y Gmail — planificado)
- CI/CD: GitHub Actions (lint backend con Ruff, lint frontend con ESLint, type-check con TypeScript)

---

## 5. Qué se construyó (funcionalidades implementadas)

### 5.1 Pipeline de ingesta de conocimiento
Script CLI propio (`ingest_data.py`) que procesa **PDFs y páginas web** como fuentes de conocimiento, con:
- Chunking semántico (500 caracteres, overlap de 80, separación respetando encabezados Markdown).
- Clasificación automática por categoría temática (6 categorías: hooks/retención, estrategia de contenido, plataformas/algoritmos, monetización, SEO/AI search, storytelling/copywriting).
- Detección de idioma y enriquecimiento de metadata por chunk.
- Generación de embeddings (3072 dimensiones) e indexado en Qdrant.

### 5.2 Chat con RAG conversacional (CRAG)
Pipeline de *Corrective RAG* con:
- Reescritura de la consulta del usuario a partir del historial (*query rewriting*) para mantener conversaciones con contexto.
- Recuperación semántica en Qdrant (`top_k=4`) con filtrado por umbral de similitud (0.35).
- Fallback automático a búsqueda web (DuckDuckGo) cuando el contexto interno no alcanza el umbral de relevancia.
- Ventana deslizante de historial (últimos 6 turnos) para controlar el tamaño del contexto enviado al LLM.
- Streaming de la respuesta del LLM al frontend.

### 5.3 Autenticación
Integración completa con Supabase Auth (email/password + Google OAuth) y verificación de tokens en el backend contra Supabase (sin manejo manual de JWT), con middleware de protección de rutas tanto en frontend como backend.

### 5.4 Chat multi-conversación (multichat)
Sistema completo de conversaciones persistentes:
- CRUD completo de chats (crear, listar, obtener con mensajes, renombrar/archivar, eliminar) vía SQLAlchemy async.
- Persistencia de mensajes de usuario y del asistente en PostgreSQL.
- Generación automática de título del chat a partir del primer mensaje (usando el LLM).
- Frontend con sidebar de conversaciones, carga optimista, indicador de streaming activo, hidratación de sesión desde el backend y manejo de cancelación de stream (AbortController).
- Gestión de estado centralizada con Zustand, con pruebas de condiciones de carrera (*race conditions*) entre streaming y cambios de sesión.

### 5.5 Diseño de producto
Interfaz con estética *glassmorphism* (fondo con gradiente púrpura/azul/rosa, contenedores translúcidos con blur), tipografía Inter, burbujas de chat diferenciadas por rol, indicador de "escribiendo" y diseño responsive.

### 5.6 En diseño / con scaffolding creado, pendientes de implementación funcional
Estos módulos están **contemplados en la arquitectura y con estructura de archivos creada** (routers y agentes definidos), pero su lógica todavía no está implementada:
- Agente de onboarding conversacional (LangGraph) para levantar el perfil del creador.
- Agente generador de calendario de contenido (LangGraph).
- Endpoints y UI de calendario editable.
- Integración con n8n (sincronización a Google Calendar, recordatorios por email).

*(Marco esto explícitamente para que el CV no sobre-represente funcionalidades no terminadas — si preferís presentarlo como "roadmap definido" en vez de "pendiente", lo ajusto.)*

---

## 6. Métricas del proyecto

**Verificables directamente del repositorio:**
- ~1.700 líneas de código en el backend (Python).
- ~4.600 líneas de código en el frontend (TypeScript/TSX).
- 8 suites de test automatizadas (6 en backend con pytest, 2 en frontend con Vitest).
- Pipeline de CI con 3 checks automáticos (lint backend, lint frontend, type-check) en cada PR.
- 6 categorías de clasificación automática de contenido en el pipeline de ingesta.
- Embeddings de 3072 dimensiones por chunk indexado.
- Recuperación semántica con top-4 resultados y umbral de relevancia configurable.
- Arquitectura modular: separación en `routers/`, `services/`, `agents/`, `models/`, `schemas/` (backend) y `features/`, `shared/` (frontend).

**Para completar con datos que solo vos tenés (te los pregunto abajo):**
- [ ] Duración total del desarrollo (semanas/meses de trabajo real).
- [ ] Tamaño de la base de conocimiento ingerida (n.º de documentos/páginas/chunks).
- [ ] Latencia promedio de respuesta del chat (percibida o medida).
- [ ] Si hubo despliegue a producción, entorno de hosting y uptime.
- [ ] Si hubo usuarios de prueba/beta y feedback cuantificable.

---

## 7. Retos técnicos destacables (para storytelling de CV)

- Diseño de un pipeline **CRAG** (Corrective RAG) con reescritura de consultas y fallback a búsqueda web, en vez de un RAG ingenuo de un solo paso.
- Migración de un flujo de autenticación basado en JWT decodificado manualmente a verificación delegada en Supabase Auth (adopción del nuevo esquema de API keys `sb_publishable_` / `sb_secret_`).
- Manejo de estado complejo en frontend para streaming de respuestas LLM con soporte de cancelación y múltiples sesiones de chat simultáneas, incluyendo tests específicos de condiciones de carrera.
- Diseño de esquema de datos relacional (PostgreSQL vía SQLAlchemy 2.0 async + Alembic) coexistiendo con una base vectorial (Qdrant) para separar claramente datos transaccionales de datos de recuperación semántica.

---

## 8. Estado actual

Fases completadas: infraestructura base, autenticación, chat con RAG y sistema multichat persistente.
Fases en el roadmap, no implementadas aún: onboarding conversacional con agente, generación de calendario de contenido con IA, integración con n8n (Google Calendar/Gmail), landing page pública y despliegue a producción.
