# Rediseño del README de perfil — Diseño

> Fecha: 2026-07-29 · Autor: Mathias Torres
> Objetivo: modernizar el README de perfil de GitHub (`MathiasTL/MathiasTL`) con un
> diseño llamativo y animado, información más rica de los proyectos, y una animación
> "dot-matrix" a medida para los proyectos destacados.

---

## 1. Objetivo y alcance

**Meta:** transformar el README actual en una carta de presentación moderna, con
animaciones, tarjetas de proyecto ricas (con métricas reales) y un banner dot-matrix
animado por cada proyecto destacado.

**Tono elegido:** llamativo y animado.

**Dentro de alcance:**
- Reescritura completa de `README.md`.
- Generador de SVGs dot-matrix animados (3 archivos en `assets/`).
- Workflow de GitHub Action para la snake animation.

**Fuera de alcance (YAGNI):**
- Screenshots/GIFs de proyectos (decisión del usuario: harían el README demasiado largo).
- Blog, certificaciones, Spotify now-playing (no solicitados).
- Rediseño de repos individuales.

---

## 2. Estructura del README (de arriba a abajo)

| # | Sección | Contenido |
|---|---------|-----------|
| 1 | **Header** | Typing SVG grande (nombre + roles rotando) sobre gradiente; badges de contacto centrados (LinkedIn, Gmail, Instagram, TikTok). |
| 2 | **Divisor wave** | SVG de onda animada como separador. |
| 3 | **💫 About Me** | Versión pulida del actual + línea "🌱 Currently building" (Puntualo, Eissential) + ubicación (Lima, Perú). |
| 4 | **🚀 Featured Projects** | 3 tarjetas, cada una con **título dot-matrix animado** + descripción + stack + métricas reales + botones de links. |
| 5 | **📂 More Projects** | Tabla compacta de 4 proyectos con links. |
| 6 | **🛠️ Tech Stack** | Iconos vía skillicons.dev agrupados por categoría. |
| 7 | **🐍 Snake** | Animación come-contribuciones (generada por Action). |
| 8 | **📊 GitHub Stats** | Stats + top langs + streak (tema `react`). |
| 9 | **📈 Contribution Graph** | Gráfico de actividad animado. |
| 10 | **Footer** | Typing SVG de cierre + quote + contador de visitas. |

---

## 3. Proyectos destacados (tarjetas ricas)

Cada tarjeta: título dot-matrix animado (SVG) + una línea de pitch + stack en `code` +
2-3 bullets de métricas/logros **reales** + botones de links.

### 3.1 Puntualo
- **Pitch:** Plataforma EdTech de reputación docente — datos en lugar de rumores.
- **Rol:** Full-Stack (Backend/IA), ~40% de commits, responsable único de la capa de IA.
- **Stack:** `Next.js 16` `FastAPI` `PostgreSQL+pgvector` `Celery` `Cohere` `Gemini`
- **Métricas reales:** SUS 87.5/100 · load test 0% error, p95 1.4s (50 usuarios) · asistente
  RAG con grounding anti-alucinación · validación docente contra 4 fuentes externas.
- **Links:** Repo `MiguelGironAltamirano/Puntualo` · 🟢 Live Demo `puntualo.vercel.app`

### 3.2 ContentSpark
- **Pitch:** Plataforma SaaS GenAI para creadores de contenido con RAG correctivo (CRAG).
- **Rol:** Individual, full-stack / AI engineer end-to-end.
- **Stack:** `FastAPI` `LangGraph` `Groq` `Gemini` `Qdrant` `Supabase` `Next.js 16`
- **Métricas reales:** pipeline CRAG con query-rewriting + fallback web · ~6.300 LOC ·
  8 suites de test · CI con 3 checks · embeddings 3072-dim.
- **Links:** Repo `MathiasTL/ContentSpark-RAG` (sin demo)

### 3.3 ProfAI
- **Pitch:** Tutor de IA multiagente para aprender Prompt Engineering (2º Hack-Nation 2025).
- **Rol:** Liderazgo e integración · dataset y pipeline RAG · frontend de entrada. Equipo de 3, 48h.
- **Stack:** `Next.js 15` `Flask` `LangGraph` `Azure OpenAI` `Azure AI Search` `PostgreSQL`
- **Métricas reales:** 8 agentes especializados · 13 lecciones · pipeline OCR→chunk→índice
  idempotente con cuarentena · 4 servicios Azure integrados.
- **Links:** Repo `NickSalA/Hackaton-06-2025` *(pendiente de confirmar por el usuario)*

---

## 4. More Projects (tabla compacta)

| Proyecto | Qué es | Links |
|----------|--------|-------|
| **AgentUP** | Agente RAG sobre documentación corporativa, desplegado en GCP Cloud Run | Repo `MathiasTL/AgentUP` · 🟢 Live Demo |
| **Eissential** | Web de productividad que fusiona SMART + Eisenhower + Kanban (individual) | Repo *(pendiente)* |
| **FoodLinks** | App móvil de rescate de alimentos (React Native/Expo), mide CO₂ evitado | Repo *(pendiente)* |
| **SMART** | Plataforma de reservas de locales con Oracle DB (académico fullstack) | Repo *(pendiente)* |

*Nota: URLs de repos pendientes se dejan como placeholder editable o se omite el botón.*

---

## 5. Animación dot-matrix (componente a medida)

**Requisito del usuario:** el nombre de cada proyecto destacado se forma con puntos,
letra por letra (efecto typing), se mantiene unos segundos, se desvanece y vuelve a
formarse, en bucle. Uno por tarjeta.

**Enfoque técnico:**
- GitHub no ejecuta JS en el README, pero **sí anima SVG con SMIL** cuando el SVG se
  embebe vía `<img>` (mismo mecanismo que readme-typing-svg y la snake).
- Se define una **fuente dot-matrix 5×7** (mapa de puntos encendidos por carácter) en un
  generador. El generador produce un SVG por nombre con:
  - Un `<circle>` por punto "encendido" de cada letra.
  - Animación SMIL de `opacity` (0→1) escalonada por columnas de izquierda a derecha
    (efecto typing), con `begin` incremental por letra.
  - Fase de "hold" (opacidad 1) y luego "fade out" (1→0).
  - `repeatCount="indefinite"` sobre un ciclo maestro para el bucle infinito.
- **Salida:** `assets/puntualo.svg`, `assets/contentspark.svg`, `assets/profai.svg`.
- **Generador:** un script (Python, sin dependencias externas) versionado en
  `scripts/gen_dotmatrix.py` para poder regenerar/ajustar. Los `.svg` resultantes se
  commitean (el README referencia los `.svg`, no ejecuta el script).

**Parámetros de diseño:**
- Color de puntos: acento de marca (`#58A6FF` u otro a definir); apagados = no se dibujan.
- Radio de punto y espaciado ajustables como constantes del generador.
- Tema: color fijo que se ve bien en tema claro y oscuro de GitHub (evitar negro puro).

**Riesgo/validación:** confirmar que el SVG SMIL anima correctamente al referenciarlo
desde el README (vía raw.githubusercontent + camo). Plan B si no animara vía `<img>`:
usar readme-typing-svg con una fuente monospace como fallback (menos fiel a la idea).

---

## 6. Snake animation (GitHub Action)

- Workflow `.github/workflows/snake.yml` usando `Platane/snk`.
- Genera `github-contribution-grid-snake.svg` (light) y `-dark.svg` en una branch `output`.
- Corre en `push` a main + `schedule` (cron ~cada 12-24h) + `workflow_dispatch`.
- El README referencia los SVG generados con soporte claro/oscuro
  (`#gh-dark-mode-only` / `#gh-light-mode-only`).
- Requiere GitHub Actions habilitado (activo por defecto).

---

## 7. Tech Stack (skillicons)

Migrar los badges de shields.io a `skillicons.dev` agrupados por categoría:
- **Languages:** python, ts, js, java, cpp, html, css
- **GenAI & Data:** (langchain/openai vía badge donde skillicons no tenga icono) + numpy, pandas, sklearn
- **Fullstack:** nextjs, react, fastapi, tailwind
- **Databases & Cloud:** mysql, postgres, oracle (badge), azure, gcp, supabase
- **Tools:** git, github, docker, figma, notion, jira

*Nota:* skillicons no cubre todo (LangChain, Oracle, LangGraph); esos se mantienen como
badge shields.io para no perder cobertura. Mezcla pragmática.

---

## 8. Archivos afectados

- `README.md` — reescritura completa.
- `assets/puntualo.svg`, `assets/contentspark.svg`, `assets/profai.svg` — nuevos.
- `scripts/gen_dotmatrix.py` — nuevo generador.
- `.github/workflows/snake.yml` — nuevo workflow.
- Los 6 `.md` de proyectos en la raíz son material fuente; **no se borran en este spec**
  (decisión posterior del usuario si moverlos a `docs/`).

---

## 9. Criterios de aceptación

1. README renderiza sin errores en GitHub, sin scroll horizontal, legible en móvil.
2. Los 3 SVGs dot-matrix animan en bucle (typing → hold → fade) al verlos en el README.
3. Snake animation configurada y generándose vía Action.
4. Todas las métricas mostradas son **reales** (las proyectadas se omiten o se marcan).
5. Links de repos/demos correctos; placeholders claramente editables donde falte URL.
6. Soporte tema claro/oscuro en las imágenes que lo permitan.
